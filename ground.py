"""Ground based telemetry reception and saving script"""
import logging
from queue import Queue
from threading import Lock, Thread

from whitevest.ground_threads import (
    replay_telemetry,
    telemetry_dashboard_server,
    telemetry_log_writing_loop,
    telemetry_reception_loop,
    telemetry_streaming_server,
)
from whitevest.lib.safe_buffer import SafeBuffer

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

    STREAMING_SERVER_PORT = os.getenv("STREAMING_PORT", 5678)
    STREAMING_SERVER_THREAD = Thread(
        target=telemetry_streaming_server,
        args=(DATA_BUFFER, STREAMING_SERVER_PORT),
        daemon=True,
    )
    STREAMING_SERVER_THREAD.start()

    SERVER_PORT = os.getenv("DASHBOARD_PORT", 8000)
    DASHBOARD_SERVER_THREAD = Thread(
        target=telemetry_dashboard_server, args=(SERVER_PORT,), daemon=True
    )
    DASHBOARD_SERVER_THREAD.start()

    REPLAY_DATA = os.getenv("REPLAY_DATA")
    if REPLAY_DATA:
        replay_telemetry(NEW_DATA_QUEUE, REPLAY_DATA)
    else:
        telemetry_reception_loop(NEW_DATA_QUEUE)
