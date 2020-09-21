"""Ground based telemetry reception and saving script"""
import asyncio
import csv
import json
import logging
import os
import struct
import sys
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from queue import Queue
from threading import Lock, Thread

import adafruit_rfm9x
import board
import busio
import digitalio
import websockets
import websockets.exceptions
from digitalio import DigitalInOut


class SafeBuffer:
    """Thread-safe buffer to store received telemetry"""

    def __init__(self):
        """Initialize the buffer"""
        self.data_buffer = list()
        self.lock = Lock()

    def append(self, reading):
        """Append new data"""
        with self.lock:
            self.data_buffer.append(reading)

    def get_range(self, start, end):
        """Get a specific range of data from the buffer"""
        logging.debug("Sending %d to %d", start, end)
        with self.lock:
            return self.data_buffer[start:end]

    def size(self):
        """Get the buffer size"""
        with self.lock:
            return len(self.data_buffer)


def init_receiver():
    """Initialize the telemetry receiver"""
    logging.info("Initializing receiver")
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = DigitalInOut(board.CE1)
    reset = DigitalInOut(board.D25)
    rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0, baudrate=1000000)
    return rfm9x


def telemetry_reception_loop(new_data_queue):
    """Loop forever reading telemetry and passing to the processing queue"""
    try:
        logging.info("Starting telemetry reading loop")
        logging.info("Will use real altimeter data")
        rfm9x = init_receiver()
        while True:
            try:
                packet = rfm9x.receive()
                if packet:
                    info = struct.unpack("ffffffffff", packet)
                    logging.debug(info)
                    new_data_queue.put((*info, rfm9x.last_rssi))
                time.sleep(0)
            except Exception as ex:
                logging.error("Telemetry point reading failure: %s", str(ex))
                logging.exception(ex)
    except Exception as ex:
        logging.error("Telemetry reading failure: %s", str(ex))
        logging.exception(ex)


def telemetry_log_writing_loop(new_data_queue, data_buffer):
    """Loop forever clearing the data queue"""
    try:
        logging.info("Starting telemetry log writing loop")
        start_time = time.time()
        with open(f"data/telemetry_log_{int(start_time)}.csv", "w") as outfile:
            while True:
                try:
                    if not new_data_queue.empty():
                        info = new_data_queue.get()
                        data_buffer.append(info)
                        row_str = ",".join([str(v) for v in info])
                        logging.debug(row_str)
                        outfile.write(row_str + "\n")
                    time.sleep(0)
                except Exception as ex:
                    logging.error("Telemetry log line writing failure: %s", str(ex))
                    logging.exception(ex)
    except Exception as ex:
        logging.error("Telemetry log writing failure: %s", str(ex))
        logging.exception(ex)


def telemetry_streaming_server(data_buffer):
    """Serve the data_buffer over websocket"""

    async def data_stream(websocket, path):
        """Handle a connection on a websocket"""
        try:
            logging.info("Client connected to streaming server")
            last_index = 0
            while True:
                if websocket.closed:
                    return
                end_index = data_buffer.size()
                if end_index > last_index:
                    await websocket.send(
                        json.dumps(data_buffer.get_range(last_index, end_index))
                    )
                    last_index = end_index
                await asyncio.sleep(1)
        except websockets.exceptions.ConnectionClosed:
            logging.info("Client disconnected from streaming server")
        except Exception as ex:
            logging.error("Telemetry streaming server failure: %s", str(ex))
            logging.exception(ex)

    try:
        logging.info("Starting telemetry streaming server")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(
            data_stream, "0.0.0.0", os.getenv("STREAMING_PORT", 5678)
        )
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    except websockets.exceptions.ConnectionClosed:
        logging.info("Client disconnected from streaming server")
    except Exception as ex:
        logging.error("Telemetry streaming server failure: %s", str(ex))
        logging.exception(ex)


def telemetry_dashboard_server():
    """Serve the static parts of the dashboard visualization"""
    try:
        logging.info("Starting telemetry dashboard server")
        httpd = HTTPServer(
            ("0.0.0.0", os.getenv("DASHBOARD_PORT", 8000)), SimpleHTTPRequestHandler
        )
        httpd.serve_forever()
    except Exception as ex:
        logging.error("Telemetry dashboard server failure: %s", str(ex))
        logging.exception(ex)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    # Queue to manage data synchronization between telemetry reception and data logging
    NEW_DATA_QUEUE = Queue()
    # List to cache processed telemetry readings
    DATA_BUFFER = SafeBuffer()

    WRITE_THREAD = Thread(
        target=telemetry_log_writing_loop,
        args=(
            NEW_DATA_QUEUE,
            DATA_BUFFER,
        ),
        daemon=True,
    )
    WRITE_THREAD.start()

    STREAMING_SERVER_THREAD = Thread(
        target=telemetry_streaming_server, args=(DATA_BUFFER,), daemon=True
    )
    STREAMING_SERVER_THREAD.start()

    DASHBOARD_SERVER_THREAD = Thread(target=telemetry_dashboard_server, daemon=True)
    DASHBOARD_SERVER_THREAD.start()

    telemetry_reception_loop(NEW_DATA_QUEUE)
