"""Inboard data capture and transmission script"""
import os
import time
from queue import Queue
from threading import Thread

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.configuration import Configuration
from whitevest.lib.utils import create_gps_thread
from whitevest.threads.air import (
    camera_thread,
    sensor_log_writing_loop,
    sensor_reading_loop,
    transmitter_thread,
)

def main():
    # Load up the system configuration
    configuration = Configuration(
        os.getenv("AIR_CONFIG_FILE", None), Configuration.default_air_configuration
    )

    # Queue to manage data synchronization between sensor reading, transmission, and data logging
    data_queue = Queue()

    # Timestamp to use for log files and log saving cutoff
    start_time = time.time()

    # Thread safe place to store altitude reading
    current_reading = AtomicValue()

    # Holds the most recent GPS data
    gps_value = AtomicValue((0.0, 0.0, 0.0, 0.0))

    gps_thread = create_gps_thread(configuration, gps_value)
    gps_thread.start()

    write_thread = Thread(
        target=sensor_log_writing_loop,
        args=(configuration, start_time, data_queue),
        daemon=True,
    )
    write_thread.start()

    camera_thread_handle = Thread(
        target=camera_thread,
        args=(configuration, start_time),
        daemon=True,
    )
    camera_thread_handle.start()

    transmitter_thread_handle = Thread(
        target=transmitter_thread,
        args=(
            configuration,
            start_time,
            current_reading,
        ),
        daemon=True,
    )
    transmitter_thread_handle.start()

    sensor_reading_loop(
        configuration, start_time, current_reading, data_queue, gps_value
    )

if __name__ == "__main__":
    main()
