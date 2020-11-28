"""Ground based telemetry serverer threads"""
import asyncio
import json
import logging
from http.server import HTTPServer

import websockets
import websockets.exceptions

from whitevest.lib.buffer_session_store import BufferSessionStore
from whitevest.lib.ground import ground_http_class_factory


def telemetry_streaming_server(port: int, buffer_session_store: BufferSessionStore):
    """Serve the active buffer over websocket"""

    async def data_stream(websocket, _):
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
        except Exception as ex:  # pylint: disable=broad-except
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
    except Exception as ex:  # pylint: disable=broad-except
        logging.error("Telemetry streaming server failure: %s", str(ex))
        logging.exception(ex)


def telemetry_dashboard_server(port: int, buffer_session_store: BufferSessionStore):
    """Serve the static parts of the dashboard visualization"""
    try:
        logging.info("Starting telemetry dashboard server")
        buffer_session_store.initialize()
        klass = ground_http_class_factory(buffer_session_store)
        httpd = HTTPServer(("0.0.0.0", port), klass)
        httpd.serve_forever()
    except Exception as ex:  # pylint: disable=broad-except
        logging.error("Telemetry dashboard server failure: %s", str(ex))
        logging.exception(ex)
