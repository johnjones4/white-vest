"""Functions for the ground runtime"""
import json
import logging
import mimetypes
import os.path
import posixpath
import struct
from http.server import BaseHTTPRequestHandler
from queue import Queue

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.buffer_session_store import BufferSessionStore
from whitevest.lib.const import TELEMETRY_STRUCT_STRING
from whitevest.lib.utils import handle_exception

if not mimetypes.inited:
    mimetypes.init()  # try to read system mime.types
EXTENSIONS_MAP = mimetypes.types_map.copy()
EXTENSIONS_MAP.update(
    {
        "": "application/octet-stream",  # Default
        ".py": "text/plain",
        ".c": "text/plain",
        ".h": "text/plain",
    }
)


def digest_next_ground_reading(rfm9x, new_data_queue: Queue, gps_value: AtomicValue):
    """Read from the radio and the GPS and put the info in a queue"""
    packet = rfm9x.receive()
    if packet:
        info = struct.unpack(TELEMETRY_STRUCT_STRING, packet)
        logging.debug(info)
        gps_info = gps_value.get_value()
        new_data_queue.put((*info, rfm9x.last_rssi, *gps_info))


def guess_type(path) -> str:
    """Guess the MIME type for a path/file"""
    _, ext = posixpath.splitext(path)
    if ext in EXTENSIONS_MAP:
        return EXTENSIONS_MAP[ext]
    ext = ext.lower()
    if ext in EXTENSIONS_MAP:
        return EXTENSIONS_MAP[ext]
    return EXTENSIONS_MAP[""]


def ground_http_class_factory(
    buffer_session_store: BufferSessionStore,
) -> BaseHTTPRequestHandler:
    """Generate a class to handle HTTP requests"""

    class TelemetryHttpRequestHandler(BaseHTTPRequestHandler):
        """Class to process HTTP requests"""

        def send_file(self, path):
            """Send a file based on the request path"""
            with open(os.path.join("dashboard/build", self.path[1:]), "r") as file:
                self.send_response(200)
                self.send_header("Content-type", guess_type(path))
                self.end_headers()
                self.wfile.write(file.read().encode("utf-8"))

        def send_json(self, info, status=200):
            """Send a JSON response"""
            self.send_response(status)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(info).encode("utf-8"))

        def do_GET(self):  # pylint: disable=invalid-name
            """Handle a GET request"""
            if self.path.startswith("/api/session/"):
                try:
                    session = int(self.path[13:])
                    self.send_json(buffer_session_store.load_session(session))
                except Exception as ex:  # pylint: disable=broad-except
                    handle_exception("Telemetry load failure", ex)
                    self.send_json({"message": "Could not load session"}, 500)
                return
            if self.path == "/api/session":
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

    return TelemetryHttpRequestHandler
