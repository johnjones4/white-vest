"""Inboard data capture and transmission threads"""
import logging
import os.path
import time
from queue import Queue

import board

from whitevest.lib.air import (
    digest_next_sensor_reading,
    transmit_latest_readings,
    write_sensor_log,
)
from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.const import TESTING_MODE
from whitevest.lib.hardware import (
    init_altimeter,
    init_magnetometer_accelerometer,
    init_radio,
)
from whitevest.lib.utils import handle_exception

if not TESTING_MODE:
    import picamera  # pylint: disable=import-error


def sensor_reading_loop(
    start_time: float,
    current_reading: AtomicValue,
    data_queue: Queue,
    gps_value: AtomicValue,
):
    """Read from the sensors on and infinite loop and queue it for transmission and logging"""
    try:
        logging.info("Starting sensor measurement loop")
        bmp = init_altimeter()
        mag, accel = init_magnetometer_accelerometer()
        while True:
            try:
                digest_next_sensor_reading(
                    start_time, bmp, gps_value, accel, mag, data_queue, current_reading
                )
            except Exception as ex:  # pylint: disable=broad-except
                handle_exception("Telemetry measurement point reading failure", ex)
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Telemetry measurement point reading failure", ex)


def sensor_log_writing_loop(
    start_time: float, runtime_limit: float, data_queue: Queue, output_directory: str
):
    """Loop through clearing the data queue until RUNTIME_LIMIT has passed"""
    try:
        logging.info("Starting sensor log writing loop")
        with open(
            os.path.join(output_directory, f"sensor_log_{int(start_time)}.csv"), "w"
        ) as outfile:
            write_sensor_log(start_time, runtime_limit, outfile, data_queue)
        logging.info("Telemetry log writing loop complete")
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Telemetry log line writing failure", ex)


def camera_thread(start_time: float, runtime_limit: float, output_directory: str):
    """Start the camera and log the video"""
    try:
        logging.info("Starting video capture")
        camera = picamera.PiCamera(framerate=90)
        camera.start_recording(
            os.path.join(output_directory, f"video_{int(start_time)}.h264")
        )
        camera.wait_recording(runtime_limit)
        camera.stop_recording()
        logging.info("Video capture complete")
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Video capture failure", ex)


def transmitter_thread(start_time: float, current_reading: AtomicValue):
    """Transmit the latest data"""
    try:
        rfm9x = init_radio(
            board.SCK_1, board.MOSI_1, board.MISO_1, board.D24, board.CE0
        )
        last_check = time.time()
        readings_sent = 0
        while True:
            try:
                last_check, readings_sent = transmit_latest_readings(
                    rfm9x,
                    last_check,
                    readings_sent,
                    start_time,
                    current_reading,
                )
            except Exception as ex:  # pylint: disable=broad-except
                handle_exception("Transmitter failure", ex)
            time.sleep(0)
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Transmitter failure", ex)
