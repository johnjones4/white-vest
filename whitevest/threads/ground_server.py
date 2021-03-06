"""Ground based telemetry serverer threads"""
import asyncio
import json
import logging

import websockets
import websockets.exceptions

from whitevest.lib.configuration import Configuration
from whitevest.lib.safe_buffer import SafeBuffer


def telemetry_streaming_server(configuration: Configuration, buffer: SafeBuffer):
    """Serve the active buffer over websocket"""

    async def data_stream(websocket, _):
        """Handle a connection on a websocket"""
        try:
            logging.info("Client connected to streaming server")
            last_index = 0
            while True:
                if websocket.closed:
                    return
                end_index = buffer.size()
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
    except Exception as ex:  # pylint: disable=broad-except
        logging.error("Telemetry streaming server failure: %s", str(ex))
        logging.exception(ex)
