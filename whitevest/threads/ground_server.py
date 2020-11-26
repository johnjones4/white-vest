import asyncio
import json
import logging
import mimetypes
import os.path
import posixpath
from http.server import BaseHTTPRequestHandler, HTTPServer

import websockets
import websockets.exceptions

from whitevest.lib.buffer_session_store import BufferSessionStore


def telemetry_streaming_server(port: int, buffer_session_store: BufferSessionStore):
    """Serve the active buffer over websocket"""

    async def data_stream(websocket, path):
        """Handle a connection on a websocket"""
        try:
            logging.info("Client connected to streaming server")
            last_index = 0
            while True:
                if websocket.closed:
                    return
                end_index = buffer_session_store.buffer.size()
                if end_index > last_index:
                    await websocket.send(
                        json.dumps(
                            buffer_session_store.buffer.get_range(last_index, end_index)
                        )
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


def telemetry_dashboard_server(port: int, buffer_session_store: BufferSessionStore):
    """Serve the static parts of the dashboard visualization"""
    try:
        buffer_session_store.initialize()

        if not mimetypes.inited:
            mimetypes.init()  # try to read system mime.types
        extensions_map = mimetypes.types_map.copy()
        extensions_map.update(
            {
                "": "application/octet-stream",  # Default
                ".py": "text/plain",
                ".c": "text/plain",
                ".h": "text/plain",
            }
        )

        class TelemetryHttpRequestHandler(BaseHTTPRequestHandler):
            def guess_type(self, path):
                base, ext = posixpath.splitext(path)
                if ext in extensions_map:
                    return extensions_map[ext]
                ext = ext.lower()
                if ext in extensions_map:
                    return extensions_map[ext]
                else:
                    return extensions_map[""]

            def send_file(self, path):
                with open(os.path.join("dashboard/build", self.path[1:]), "r") as file:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(file.read().encode("utf-8"))

            def send_json(self, info, status=200):
                self.send_response(status)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(info).encode("utf-8"))

            def do_GET(self):
                if self.path.startswith("/api/session/"):
                    try:
                        session = int(self.path[13:])
                        self.send_json(buffer_session_store.load_session(session))
                    except Exception as ex:
                        print(ex)
                        self.send_json({"message": "Could not load session"}, 500)
                    return
                elif self.path == "/api/session":
                    self.send_json(buffer_session_store.get_sessions())
                    return
                try:
                    if self.path.endswith("/"):
                        self.send_file("index.html")
                    elif "/../" not in posixpath.basename(self.path):
                        self.send_file(self.path)
                except OSError:
                    if self.path != "/":
                        self.send_file("index.html")
                    else:
                        self.send_json({"message": "Static file cannot be read"}, 500)

            def do_POST(self):
                if self.path == "/api/session":
                    buffer_session_store.create_new_session()
                    self.send_json({"message": "ok"})

        logging.info("Starting telemetry dashboard server")
        httpd = HTTPServer(("0.0.0.0", port), TelemetryHttpRequestHandler)
        httpd.serve_forever()
    except Exception as ex:
        logging.error("Telemetry dashboard server failure: %s", str(ex))
        logging.exception(ex)
