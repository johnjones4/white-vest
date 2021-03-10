"""Ground based telemetry reception and saving script"""
import os
from threading import Thread

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.configuration import Configuration
from whitevest.lib.const import TESTING_MODE
from whitevest.lib.safe_buffer import SafeBuffer
from whitevest.lib.utils import create_gps_thread
from whitevest.threads.ground_data import replay_telemetry, telemetry_reception_loop
from whitevest.threads.ground_server import telemetry_streaming_server, telemetry_rest_server


def main():
    """Ground based telemetry reception and saving script"""

    # Load up the system configuration
    configuration = Configuration(
        os.getenv("GROUND_CONFIG_FILE", None),
        Configuration.default_ground_configuration,
    )

    # Make a buffer
    buffer = SafeBuffer()

    # Holds the most recent GPS data
    gps_value = AtomicValue((0.0, 0.0, 0.0, 0.0))

    if not TESTING_MODE:
        gps_thread = create_gps_thread(configuration, gps_value)
        gps_thread.start()

    streaming_server_thread = Thread(
        target=telemetry_streaming_server,
        args=(
            configuration,
            buffer,
        ),
        daemon=True,
    )
    streaming_server_thread.start()

    rest_server_thread = Thread(
        target=telemetry_rest_server,
        args=(
            configuration,
            buffer,
        ),
        daemon=True,
    )
    rest_server_thread.start()

    if TESTING_MODE:
        replay_telemetry(buffer, os.getenv("REPLAY_DATA"))
    else:
        telemetry_reception_loop(
            configuration,
            buffer,
            gps_value,
        )


if __name__ == "__main__":
    main()
