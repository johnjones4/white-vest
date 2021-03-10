"""Ground based telemetry serverer threads"""
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging

import websockets
import websockets.exceptions

from whitevest.lib.configuration import Configuration
from whitevest.lib.safe_buffer import SafeBuffer
from whitevest.lib.utils import handle_exception


def telemetry_streaming_server(configuration: Configuration, buffer: SafeBuffer):
    """Serve the active buffer over websocket"""

    async def data_stream(websocket, _):
        """Handle a connection on a websocket"""
        try:
            logging.info("Client connected to streaming server")
            last_index = 0
            while True:
                if websocket.closed:
                    logging.info("Client disconnected from streaming server")
                    return
                end_index = buffer.size()
                if end_index < last_index:
                    last_index = 0
                if end_index > last_index:
                    await websocket.send(
                        json.dumps(buffer.get_range(last_index, end_index))
                    )
                    last_index = end_index
                await asyncio.sleep(1)
        except websockets.exceptions.ConnectionClosed:
            logging.info("Client disconnected from streaming server")
        except Exception as ex:  # pylint: disable=broad-except
            logging.error("Telemetry streaming server failure: %s", str(ex))
            logging.exception(ex)

    try:
        logging.info("Starting telemetry streaming server")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(
            data_stream, "0.0.0.0", configuration.get("streaming_server_port")
        )
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    except websockets.exceptions.ConnectionClosed:
        logging.info("Client disconnected from streaming server")
    except Exception as ex: # pylint: disable=broad-except
        handle_exception("Telemetry streaming server failure", ex)


def telemetry_rest_server(configuration: Configuration, buffer: SafeBuffer):
    """Start a basic REST server for control"""
    try:
        class TelemetryHttpRequestHandler(BaseHTTPRequestHandler):
            def send_json(self, info, status=200):
                self.send_response(status)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(info).encode("utf-8"))

            def do_OPTIONS(self):
                self.send_response(200, "ok")
                self.send_header('Access-Control-Allow-Credentials', 'true')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")

            def do_POST(self):
                if self.path == "/reset":
                    buffer.purge()
                    self.send_json({"message": "ok"})
                    return
                self.send_json({"message": "no-op"})

        logging.info("Starting telemetry dashboard server")
        httpd = HTTPServer(("0.0.0.0", configuration.get("http_server_port")), TelemetryHttpRequestHandler)
        httpd.serve_forever()
    except Exception as ex: # pylint: disable=broad-except
        handle_exception("Telemetry dashboard server failure", ex)
