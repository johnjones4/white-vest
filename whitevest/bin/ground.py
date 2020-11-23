"""Ground based telemetry reception and saving script"""
from queue import Queue
from threading import Lock, Thread
import os
import time

from whitevest.threads.ground_data import (
    replay_telemetry,
    telemetry_log_writing_loop,
    telemetry_reception_loop,
)
from whitevest.threads.ground_server import (
    telemetry_dashboard_server,
    telemetry_streaming_server,
)
from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.buffer_session_store import BufferSessionStore

if __name__ == "__main__":
    # Queue to manage data synchronization between telemetry reception and data logging
    NEW_DATA_QUEUE = Queue()
    # Manages the data buffers
    BUFFER_SESSION_STORE = BufferSessionStore()

    WRITE_THREAD = Thread(
        target=telemetry_log_writing_loop,
        args=(
            NEW_DATA_QUEUE,
            BUFFER_SESSION_STORE,
        ),
        daemon=True,
    )
    WRITE_THREAD.start()

    STREAMING_SERVER_PORT = int(os.getenv("STREAMING_PORT", 5678))
    STREAMING_SERVER_THREAD = Thread(
        target=telemetry_streaming_server,
        args=(STREAMING_SERVER_PORT, BUFFER_SESSION_STORE, ),
        daemon=True,
    )
    STREAMING_SERVER_THREAD.start()

    SERVER_PORT = int(os.getenv("DASHBOARD_PORT", 8000))
    DASHBOARD_SERVER_THREAD = Thread(
        target=telemetry_dashboard_server, args=(SERVER_PORT, BUFFER_SESSION_STORE, ), daemon=True
    )
    DASHBOARD_SERVER_THREAD.start()

    REPLAY_DATA = os.getenv("REPLAY_DATA")
    if REPLAY_DATA:
        replay_telemetry(NEW_DATA_QUEUE, REPLAY_DATA)
    else:
        telemetry_reception_loop(NEW_DATA_QUEUE)
