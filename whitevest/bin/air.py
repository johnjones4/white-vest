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

if __name__ == "__main__":
    # Load up the system configuration
    CONFIGURATION = Configuration(
        os.getenv("AIR_CONFIG_FILE", "air.yml"), Configuration.default_air_configuration
    )

    # Queue to manage data synchronization between sensor reading, transmission, and data logging
    DATA_QUEUE = Queue()

    # Timestamp to use for log files and log saving cutoff
    START_TIME = time.time()

    # Thread safe place to store altitude reading
    CURRENT_READING = AtomicValue()

    # Holds the most recent GPS data
    GPS_VALUE = AtomicValue((0.0, 0.0, 0.0, 0.0))

    GPS_THREAD = create_gps_thread(CONFIGURATION, GPS_VALUE)
    GPS_THREAD.start()

    WRITE_THREAD = Thread(
        target=sensor_log_writing_loop,
        args=(CONFIGURATION, START_TIME, DATA_QUEUE),
        daemon=True,
    )
    WRITE_THREAD.start()

    CAMERA_THREAD = Thread(
        target=camera_thread,
        args=(CONFIGURATION, START_TIME),
        daemon=True,
    )
    CAMERA_THREAD.start()

    TRANSMITTER_THREAD = Thread(
        target=transmitter_thread,
        args=(
            CONFIGURATION,
            START_TIME,
            CURRENT_READING,
        ),
        daemon=True,
    )
    TRANSMITTER_THREAD.start()

    sensor_reading_loop(
        CONFIGURATION, START_TIME, CURRENT_READING, DATA_QUEUE, GPS_VALUE
    )
