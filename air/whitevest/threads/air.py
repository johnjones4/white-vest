"""Inboard data capture and transmission threads"""
import logging
import os.path
import time
from queue import Queue

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.configuration import Configuration
from whitevest.lib.const import TESTING_MODE
from whitevest.lib.hardware import (
    init_altimeter,
    init_magnetometer_accelerometer,
    init_radio,
)
from whitevest.lib.utils import (
    digest_next_sensor_reading,
    handle_exception,
    transmit_latest_readings,
    write_sensor_log,
)

if not TESTING_MODE:
    import picamera  # pylint: disable=import-error


# pylint: disable=too-many-arguments
def sensor_reading_loop(
    configuration: Configuration,
    start_time: float,
    data_queue: Queue,
    current_reading: AtomicValue,
    gps_value: AtomicValue,
    continue_running: AtomicValue,
):
    """Read from the sensors on and infinite loop and queue it for transmission and logging"""
    try:
        logging.info("Starting sensor measurement loop")
        bmp = init_altimeter(configuration)
        mag, accel = init_magnetometer_accelerometer(configuration)
        while continue_running.get_value():
            try:
                digest_next_sensor_reading(
                    start_time,
                    data_queue,
                    current_reading,
                    gps_value.get_value(),
                    bmp._read(),  # pylint: disable=protected-access
                    (*accel.acceleration, *mag.magnetic),
                )
            except Exception as ex:  # pylint: disable=broad-except
                handle_exception("Telemetry measurement point reading failure", ex)
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Telemetry measurement point reading failure", ex)


def sensor_log_writing_loop(
    configuration: Configuration,
    start_time: float,
    data_queue: Queue,
    continue_running: AtomicValue,
    continue_logging: AtomicValue,
):
    """Loop through clearing the data queue until cancelled"""
    try:
        logging.info("Starting sensor log writing loop")
        output_directory = configuration.get("output_directory")
        with open(
            os.path.join(output_directory, f"sensor_log_{int(start_time)}.csv"), "w"
        ) as outfile:
            write_sensor_log(
                start_time, outfile, data_queue, continue_running, continue_logging
            )
        logging.info("Telemetry log writing loop complete")
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Telemetry log line writing failure", ex)


def camera_thread(
    configuration: Configuration,
    start_time: float,
    continue_running: AtomicValue,
    continue_logging: AtomicValue,
):
    """Start the camera and log the video"""
    try:
        logging.info("Starting video capture")
        output_directory = configuration.get("output_directory")
        camera = picamera.PiCamera(framerate=90)
        camera.start_recording(
            os.path.join(output_directory, f"video_{int(start_time)}.h264")
        )
        while continue_running.get_value() and continue_logging.get_value():
            camera.wait_recording(1)
        camera.stop_recording()
        logging.info("Video capture complete")
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Video capture failure", ex)


def transmitter_thread(
    configuration: Configuration,
    start_time: float,
    current_reading: AtomicValue,
    pcnt_to_limit: AtomicValue,
    continue_running: AtomicValue,
):
    """Transmit the latest data"""
    try:
        rfm9x = init_radio(configuration)
        if not rfm9x:
            return
        last_check = time.time()
        readings_sent = 0
        while continue_running.get_value():
            try:
                readings_sent, last_check = transmit_latest_readings(
                    pcnt_to_limit,
                    rfm9x,
                    last_check,
                    readings_sent,
                    start_time,
                    current_reading,
                )
            except Exception as ex:  # pylint: disable=broad-except
                handle_exception("Transmitter failure", ex)
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Transmitter failure", ex)
