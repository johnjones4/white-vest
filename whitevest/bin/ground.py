"""Ground based telemetry reception and saving script"""
import os
from queue import Queue
from threading import Thread

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.buffer_session_store import BufferSessionStore
from whitevest.lib.configuration import Configuration
from whitevest.lib.const import TESTING_MODE
from whitevest.lib.utils import create_gps_thread
from whitevest.threads.ground_data import (
    replay_telemetry,
    telemetry_log_writing_loop,
    telemetry_reception_loop,
)
from whitevest.threads.ground_server import (
    telemetry_dashboard_server,
    telemetry_streaming_server,
)

if __name__ == "__main__":
    # Load up the system configuration
    CONFIGURATION = Configuration(
        os.getenv("GROUND_CONFIG_FILE", "air.yml"),
        Configuration.default_ground_configuration,
    )

    # Queue to manage data synchronization between telemetry reception and data logging
    NEW_DATA_QUEUE = Queue()

    # Manages the data buffers
    BUFFER_SESSION_STORE = BufferSessionStore(CONFIGURATION)

    # Holds the most recent GPS data
    GPS_VALUE = AtomicValue((0.0, 0.0, 0.0, 0.0))

    if not TESTING_MODE:
        GPS_THREAD = create_gps_thread(CONFIGURATION, GPS_VALUE)
        GPS_THREAD.start()

    WRITE_THREAD = Thread(
        target=telemetry_log_writing_loop,
        args=(
            NEW_DATA_QUEUE,
            BUFFER_SESSION_STORE,
        ),
        daemon=True,
    )
    WRITE_THREAD.start()

    STREAMING_SERVER_THREAD = Thread(
        target=telemetry_streaming_server,
        args=(
            CONFIGURATION,
            BUFFER_SESSION_STORE,
        ),
        daemon=True,
    )
    STREAMING_SERVER_THREAD.start()

    DASHBOARD_SERVER_THREAD = Thread(
        target=telemetry_dashboard_server,
        args=(
            CONFIGURATION,
            BUFFER_SESSION_STORE,
        ),
        daemon=True,
    )
    DASHBOARD_SERVER_THREAD.start()

    if TESTING_MODE:
        replay_telemetry(NEW_DATA_QUEUE, os.getenv("REPLAY_DATA"))
    else:
        telemetry_reception_loop(
            CONFIGURATION,
            NEW_DATA_QUEUE,
            GPS_VALUE,
        )
