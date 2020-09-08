import os
import logging
from threading import Thread
import time
from queue import Queue
import csv
import sys
import asyncio
import websockets
import websockets.exceptions
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

logging.getLogger().setLevel(logging.INFO)

# Don't import the RF library if we're in testing mode. This let's us test when not on a Raspberry Pi
if not os.getenv("TEST_DATE_FILE", False):
    from rpi_rf import RFDevice

# Queue to manage data synchronization between telemetry reception and data logging
ALTITUDE_QUEUE = Queue()
# List to cache processed telemetry readings
ALTITUDE_BUFFER = list()

def init_receiver():
    """Initialize the telemetry receiver"""
    logging.info("Initializing receiver")
    tx = RFDevice(17)
    tx.enable_rx()
    return tx

def init_testing_data():
    """Read test data from CSV"""
    mock_data = list()
    with open(os.getenv("TEST_DATE_FILE")) as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            (_, _, altitude) = row
            mock_data.append(int(float(altitude) * 100))
    return mock_data

def telemetry_reception_loop(altitude_queue):
    """Loop forever reading telemetry and passing to the processing queue"""
    try:
        logging.info("Starting telemetry reading loop")
        testing_mode = os.getenv("TEST_DATE_FILE", False)
        if testing_mode:
            logging.info("Will simulate altimeter data")
            mock_data = init_testing_data()
            mock_index = 0
        else:
            logging.info("Will use real altimeter data")
            rx = init_receiver()
        last_rx_code_timestamp = None
        while True:
            try:
                if testing_mode:
                    current_rx_code_timestamp = int(time.time() * 10)
                    if not last_rx_code_timestamp or current_rx_code_timestamp != last_rx_code_timestamp:
                        received_data = mock_data[mock_index]
                        if mock_index < len(mock_data) - 1:
                            mock_index += 1
                        else:
                            sys.exit(0)
                else:
                    current_rx_code_timestamp = rx.rx_code_timestamp
                    received_data = rx.rx_code
                if not last_rx_code_timestamp or current_rx_code_timestamp != last_rx_code_timestamp:
                    last_rx_code_timestamp = current_rx_code_timestamp
                    altitude = float(received_data) / 100.0
                    altitude_queue.put((time.time(), altitude))
                time.sleep(0)
            except Exception as ex:
                logging.error("Telemetry point reading failure: %s", str(ex))
                logging.exception(ex)
    except Exception as ex:
        logging.error("Telemetry reading failure: %s", str(ex))
        logging.exception(ex)


def write_telemetry_buffer(start_time, altitude_queue, buffer):
    """Write all queued data to the log and buffer"""
    try:
        with open(f"data/telemetry_log_{int(start_time)}.csv", "a") as outfile:
            while not altitude_queue.empty():
                try:
                    (timestamp, altitude) = altitude_queue.get()
                    buffer.append((timestamp, altitude))
                    row_str = ",".join([str(timestamp), str(altitude)])
                    logging.debug(row_str)
                    outfile.write(row_str + "\n")
                    time.sleep(0.1)
                except Exception as ex:
                    logging.error("Telemetry log line writing failure: %s", str(ex))
                    logging.exception(ex)
        time.sleep(1)
    except Exception as ex:
        logging.error("Telemetry log output writing failure: %s", str(ex))
        logging.exception(ex)


def telemetry_log_writing_loop(altitude_queue, buffer):
    """Loop forever clearing the data queue"""
    try:
        logging.info("Starting telemetry log writing loop")
        start_time = time.time()
        while True:
            write_telemetry_buffer(start_time, altitude_queue, buffer)
    except Exception as ex:
        logging.error("Telemetry log writing failure: %s", str(ex))
        logging.exception(ex)


def telemetry_streaming_server(buffer):
    """Serve the buffer over websocket"""

    async def data_stream(websocket, path):
        """Handle a connection on a websocket"""
        try:
            logging.info("Client connected to streaming server")
            last_index = 0
            while True:
                if websocket.closed:
                    return
                end_index = len(buffer)
                if end_index > last_index:
                    await websocket.send(json.dumps(buffer[last_index : end_index]))
                    last_index = end_index
                else:
                    time.sleep(1)
        except websockets.exceptions.ConnectionClosed:
            logging.info("Client disconnected from streaming server")
        except Exception as ex:
            logging.error("Telemetry streaming server failure: %s", str(ex))
            logging.exception(ex)

    try:
        logging.info("Starting telemetry streaming server")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(data_stream, "0.0.0.0", os.getenv("STREAMING_PORT", 5678))
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    except websockets.exceptions.ConnectionClosed:
        logging.info("Client disconnected from streaming server")
    except Exception as ex:
        logging.error("Telemetry streaming server failure: %s", str(ex))
        logging.exception(ex)


def telemetry_dashboard_server():
    try:
        logging.info("Starting telemetry dashboard server")
        httpd = HTTPServer(("0.0.0.0", os.getenv("DASHBOARD_PORT", 8000)), SimpleHTTPRequestHandler)
        httpd.serve_forever()
    except Exception as ex:
        logging.error("Telemetry dashboard server failure: %s", str(ex))
        logging.exception(ex)


if __name__ == "__main__":
    WRITE_THREAD = Thread(target=telemetry_log_writing_loop, args=(ALTITUDE_QUEUE, ALTITUDE_BUFFER,), daemon=True)
    WRITE_THREAD.start()

    STREAMING_SERVER_THREAD = Thread(target=telemetry_streaming_server, args=(ALTITUDE_BUFFER,), daemon=True)
    STREAMING_SERVER_THREAD.start()

    DASHBOARD_SERVER_THREAD = Thread(target=telemetry_dashboard_server, daemon=True)
    DASHBOARD_SERVER_THREAD.start()

    telemetry_reception_loop(ALTITUDE_QUEUE)
