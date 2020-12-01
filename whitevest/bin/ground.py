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

def main():
    # Load up the system configuration
    configuration = Configuration(
        os.getenv("GROUND_CONFIG_FILE", None),
        Configuration.default_ground_configuration,
    )

    # Queue to manage data synchronization between telemetry reception and data logging
    new_data_queue = Queue()

    # Manages the data buffers
    buffer_session_store = BufferSessionStore(configuration)

    # Holds the most recent GPS data
    gps_value = AtomicValue((0.0, 0.0, 0.0, 0.0))

    if not TESTING_MODE:
        gps_thread = create_gps_thread(configuration, gps_value)
        gps_thread.start()

    write_thread = Thread(
        target=telemetry_log_writing_loop,
        args=(
            new_data_queue,
            buffer_session_store,
        ),
        daemon=True,
    )
    write_thread.start()

    streaming_server_thread = Thread(
        target=telemetry_streaming_server,
        args=(
            configuration,
            buffer_session_store,
        ),
        daemon=True,
    )
    streaming_server_thread.start()

    dashboard_server_thread = Thread(
        target=telemetry_dashboard_server,
        args=(
            configuration,
            buffer_session_store,
        ),
        daemon=True,
    )
    dashboard_server_thread.start()

    if TESTING_MODE:
        replay_telemetry(new_data_queue, os.getenv("REPLAY_DATA"))
    else:
        telemetry_reception_loop(
            configuration,
            new_data_queue,
            gps_value,
        )

if __name__ == "__main__":
    main()
