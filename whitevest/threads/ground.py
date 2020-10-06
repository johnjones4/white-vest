"""Ground based telemetry reception and saving threads"""
import asyncio
import csv
import json
import logging
import struct
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

if not os.getenv("REPLAY_DATA", False):
    import board
import websockets
import websockets.exceptions

if not os.getenv("REPLAY_DATA", False):
    from whitevest.lib.hardware import init_radio


def telemetry_reception_loop(new_data_queue):
    """Loop forever reading telemetry and passing to the processing queue"""
    try:
        logging.info("Starting telemetry reading loop")
        rfm9x = init_radio(board.SCK, board.MOSI, board.MISO, board.CE1, board.D25)
        while True:
            try:
                packet = rfm9x.receive()
                if packet:
                    info = struct.unpack("fffffffff", packet)
                    logging.debug(info)
                    new_data_queue.put((*info, rfm9x.last_rssi))
                time.sleep(0)
            except Exception as ex:
                logging.error("Telemetry point reading failure: %s", str(ex))
                logging.exception(ex)
    except Exception as ex:
        logging.error("Telemetry reading failure: %s", str(ex))
        logging.exception(ex)


def replay_telemetry(new_data_queue, replay_file):
    """Replays telemetry from a file"""
    start_time = time.time()
    logging.info(f"Replaying telemetry from {replay_file}")
    with open(replay_file, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            info = [float(v) for v in row]
            while time.time() - start_time < info[0]:
                pass
            new_data_queue.put(info)
            time.sleep(0)


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


def telemetry_streaming_server(data_buffer, port):
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
        start_server = websockets.serve(data_stream, "0.0.0.0", port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    except websockets.exceptions.ConnectionClosed:
        logging.info("Client disconnected from streaming server")
    except Exception as ex:
        logging.error("Telemetry streaming server failure: %s", str(ex))
        logging.exception(ex)


def telemetry_dashboard_server(port):
    """Serve the static parts of the dashboard visualization"""
    try:
        logging.info("Starting telemetry dashboard server")
        httpd = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
        httpd.serve_forever()
    except Exception as ex:
        logging.error("Telemetry dashboard server failure: %s", str(ex))
        logging.exception(ex)
