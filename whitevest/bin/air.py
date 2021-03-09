"""Inboard data capture and transmission script"""
import os
import time
from queue import Queue
from threading import Thread

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.configuration import Configuration
from whitevest.lib.utils import create_gps_thread
from whitevest.threads.air import (
    altimeter_reading_loop,
    camera_thread,
    magnetometer_accelerometer_reading_loop,
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
    data_queue = Queue()

    # Timestamp to use for log files and log saving cutoff
    start_time = time.time()

    # Thread safe place to store altitude reading
    current_reading = AtomicValue()

    # Holds the most recent GPS data
    gps_value = AtomicValue((0.0, 0.0, 0.0, 0.0))

    # Flag that the camera is running
    camera_is_running = AtomicValue(0.0)

    altimeter_value = AtomicValue()
    altimeter_value.update((0.0, 0.0))

    magnetometer_accelerometer_value = AtomicValue()
    magnetometer_accelerometer_value.update((0.0, 0.0, 0.0, 0.0, 0.0, 0.0))

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
        args=(configuration, start_time, camera_is_running),
        daemon=True,
    )
    camera_thread_handle.start()

    transmitter_thread_handle = Thread(
        target=transmitter_thread,
        args=(configuration, start_time, current_reading, camera_is_running),
        daemon=True,
    )
    transmitter_thread_handle.start()

    altimeter_thread = Thread(
        target=altimeter_reading_loop, args=(configuration, altimeter_value)
    )
    altimeter_thread.start()

    magnetometer_accelerometer_thread = Thread(
        target=magnetometer_accelerometer_reading_loop,
        args=(configuration, magnetometer_accelerometer_value),
    )
    magnetometer_accelerometer_thread.start()

    sensor_reading_loop(
        start_time,
        data_queue,
        current_reading,
        gps_value,
        altimeter_value,
        magnetometer_accelerometer_value,
    )


if __name__ == "__main__":
    main()
