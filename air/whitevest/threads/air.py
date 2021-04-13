"""Inboard data capture and transmission threads"""
import logging
import os.path
import time
from queue import Queue

from whitevest.lib.air import (
    digest_next_sensor_reading,
    transmit_latest_readings,
    write_sensor_log,
)
from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.configuration import Configuration
from whitevest.lib.const import TESTING_MODE
from whitevest.lib.hardware import (
    init_altimeter,
    init_magnetometer_accelerometer,
    init_radio,
)
from whitevest.lib.utils import handle_exception

if not TESTING_MODE:
    import picamera  # pylint: disable=import-error


def altimeter_reading_loop(
    configuration: Configuration,
    altimeter_value: AtomicValue,
    continue_running: AtomicValue,
):
    """Continually read the altimeter and set it to the atomic var"""
    try:
        bmp = init_altimeter(configuration)
        while continue_running.get_value() and bmp:
            try:
                altimeter_value.update(bmp._read())  # pylint: disable=protected-access
            except Exception as ex:  # pylint: disable=broad-except
                handle_exception("Altimeter reading failure", ex)
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Altimeter setup failure", ex)


def magnetometer_accelerometer_reading_loop(
    configuration: Configuration,
    magnetometer_accelerometer_value: AtomicValue,
    continue_running: AtomicValue,
):
    """Continually read the accelerometer/magnetometer and set it to the atomic var"""
    try:
        mag, accel = init_magnetometer_accelerometer(configuration)
        while continue_running.get_value() and mag and accel:
            try:
                magnetometer_accelerometer_value.update(
                    (*accel.acceleration, *mag.magnetic)
                )
            except Exception as ex:  # pylint: disable=broad-except
                handle_exception("Magnetometer/Accelerometer reading failure", ex)
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Magnetometer/Accelerometer setup failure", ex)


# pylint: disable=too-many-arguments
def sensor_reading_loop(
    start_time: float,
    data_queue: Queue,
    current_reading: AtomicValue,
    gps_value: AtomicValue,
    altimeter_value: AtomicValue,
    magnetometer_accelerometer_value: AtomicValue,
    continue_running: AtomicValue,
):
    """Read from the sensors on and infinite loop and queue it for transmission and logging"""
    try:
        logging.info("Starting sensor measurement loop")
        while continue_running.get_value():
            try:
                digest_next_sensor_reading(
                    start_time,
                    data_queue,
                    current_reading,
                    gps_value,
                    altimeter_value,
                    magnetometer_accelerometer_value,
                )
                time.sleep(0.03)
            except Exception as ex:  # pylint: disable=broad-except
                handle_exception("Telemetry measurement point reading failure", ex)
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Telemetry measurement point reading failure", ex)


def sensor_log_writing_loop(
    configuration: Configuration,
    start_time: float,
    data_queue: Queue,
    continue_running: AtomicValue,
):
    """Loop through clearing the data queue until RUNTIME_LIMIT has passed"""
    try:
        logging.info("Starting sensor log writing loop")
        runtime_limit = configuration.get("runtime_limit")
        output_directory = configuration.get("output_directory")
        with open(
            os.path.join(output_directory, f"sensor_log_{int(start_time)}.csv"), "w"
        ) as outfile:
            write_sensor_log(
                start_time, runtime_limit, outfile, data_queue, continue_running
            )
        logging.info("Telemetry log writing loop complete")
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Telemetry log line writing failure", ex)


def camera_thread(
    configuration: Configuration,
    start_time: float,
    camera_is_running: AtomicValue,
    continue_running: AtomicValue,
):
    """Start the camera and log the video"""
    try:
        logging.info("Starting video capture")
        runtime_limit = configuration.get("runtime_limit")
        output_directory = configuration.get("output_directory")
        camera = picamera.PiCamera(framerate=90)
        camera_is_running.update(1.0)
        camera.start_recording(
            os.path.join(output_directory, f"video_{int(start_time)}.h264")
        )
        start = time.time()
        while continue_running.get_value() and time.time() - start <= runtime_limit:
            camera.wait_recording(1)
        camera.stop_recording()
        logging.info("Video capture complete")
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Video capture failure", ex)
    camera_is_running.update(0.0)


def transmitter_thread(
    configuration: Configuration,
    start_time: float,
    current_reading: AtomicValue,
    camera_is_running: AtomicValue,
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
                    camera_is_running,
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
