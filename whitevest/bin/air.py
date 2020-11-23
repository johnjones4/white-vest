"""Inboard data capture and transmission script"""
import os
import time
from queue import Queue
from threading import Thread

from whitevest.threads.air import (
    camera_thread,
    sensor_log_writing_loop,
    sensor_reading_loop,
    transmitter_thread,
)
from whitevest.lib.atomic_value import AtomicValue

if __name__ == "__main__":
    # How long should logging and recording run
    RUNTIME_LIMIT = int(os.getenv("RUNTIME_LIMIT", 1800))

    # Path to where to save data
    OUTPUT_DIRECTORY = os.getenv("OUTPUT_DIRECTORY", "./data")

    # Queue to manage data synchronization between sensor reading, transmission, and data logging
    DATA_QUEUE = Queue()

    # Timestamp to use for log files and log saving cutoff
    START_TIME = time.time()

    # Thread safe place to store altitude reading
    CURRENT_READING = AtomicValue()

    WRITE_THREAD = Thread(
        target=sensor_log_writing_loop,
        args=(START_TIME, RUNTIME_LIMIT, DATA_QUEUE, OUTPUT_DIRECTORY),
        daemon=True,
    )
    WRITE_THREAD.start()

    CAMERA_THREAD = Thread(
        target=camera_thread,
        args=(START_TIME, RUNTIME_LIMIT, OUTPUT_DIRECTORY),
        daemon=True,
    )
    CAMERA_THREAD.start()

    TRANSMITTER_THREAD = Thread(
        target=transmitter_thread,
        args=(
            START_TIME,
            CURRENT_READING,
        ),
        daemon=True,
    )
    TRANSMITTER_THREAD.start()

    sensor_reading_loop(START_TIME, CURRENT_READING, DATA_QUEUE)
