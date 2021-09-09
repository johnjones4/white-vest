"""Inboard data capture and transmission script"""
import logging
import os
import time
from queue import Queue
from threading import Thread

from whitevest.lib.atomic_buffer import AtomicBuffer
from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.configuration import Configuration
from whitevest.lib.hardware import init_reset_button
from whitevest.lib.utils import create_gps_thread
from whitevest.threads.air import (
    camera_thread,
    sensor_log_writing_loop,
    sensor_reading_loop,
    transmitter_thread,
)


def main():
    """Inboard data capture and transmission script"""

    # Load up the system configuration
    configuration = Configuration(
        os.getenv("AIR_CONFIG_FILE", None), Configuration.default_air_configuration
    )

    # Queue to manage data synchronization between sensor reading, transmission, and data logging
    data_queue = Queue(1000)

    # Timestamp to use for log files and log saving cutoff
    start_time = time.time()

    # Thread safe place to store altitude reading
    current_readings = AtomicBuffer(50)

    # Holds the most recent GPS data
    gps_value = AtomicValue((0.0, 0.0, 0.0, 0.0))

    # pcnt counter to runtime limit
    pcnt_to_limit = AtomicValue(0.0)

    # Thread safe place to store continue value
    continue_running = AtomicValue(True)

    # Thread safe place to store continue value
    continue_logging = AtomicValue(True)

    # Setup listener for reset button
    init_reset_button(configuration, continue_running)

    gps_thread = create_gps_thread(configuration, gps_value, continue_running)
    gps_thread.start()

    write_thread = Thread(
        target=sensor_log_writing_loop,
        args=(
            configuration,
            start_time,
            data_queue,
            continue_running,
            continue_logging,
        ),
        daemon=True,
    )
    write_thread.start()

    camera_thread_handle = Thread(
        target=camera_thread,
        args=(configuration, start_time, continue_running, continue_logging),
        daemon=True,
    )
    camera_thread_handle.start()

    transmitter_thread_handle = Thread(
        target=transmitter_thread,
        args=(
            configuration,
            start_time,
            current_readings,
            pcnt_to_limit,
            continue_running,
        ),
        daemon=True,
    )
    transmitter_thread_handle.start()

    sensor_reading_thread = Thread(
        target=sensor_reading_loop,
        args=(
            configuration,
            start_time,
            data_queue,
            current_readings,
            gps_value,
            continue_running,
        ),
        daemon=True,
    )
    sensor_reading_thread.start()

    runtime_limit = configuration.get("runtime_limit")
    while continue_running.get_value() and time.time() - start_time <= runtime_limit:
        pcnt_to_limit.update((time.time() - start_time) / runtime_limit)
        time.sleep(1)
    logging.info("Stopping write activities")
    continue_logging.update(False)

    write_thread.join()
    camera_thread_handle.join()
    pcnt_to_limit.update(1)

    logging.info("Write activities ended")

    gps_thread.join()
    transmitter_thread_handle.join()
    sensor_reading_thread.join()


if __name__ == "__main__":
    main()
