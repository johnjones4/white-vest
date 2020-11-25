"""Inboard data capture and transmission threads"""
import logging
import os.path
import struct
import time

import board
import picamera

from whitevest.lib.hardware import (
    init_altimeter,
    init_magnetometer_accelerometer,
    init_radio,
    init_gps
)

from whitevest.lib.atomic_value import AtomicValue
from queue import Queue


def sensor_reading_loop(start_time: float, current_reading: AtomicValue, data_queue: Queue, gps_value: AtomicValue):
    """Read from the sensors on and infinite loop and queue it for transmission and logging"""
    try:
        logging.info("Starting sensor measurement loop")
        bmp = init_altimeter()
        mag, accel = init_magnetometer_accelerometer()
        while True:
            try:
                (pressure, temperature) = bmp._read()
                gps = gps_value.get_value()
                info = (
                    time.time() - start_time,
                    *bmp.read(),
                    *accel.acceleration,
                    *mag.magnetic,
                    gps.latitude if gps else 0.0,
                    gps.longitude if gps else 0.0,
                    gps.gps_qual if gps else 0.0,
                    gps.num_sats if gps else 0.0
                )
                data_queue.put(info)
                current_reading.try_update(info)
            except Exception as ex:
                logging.error(
                    "Telemetry measurement point reading failure: %s", str(ex)
                )
                logging.exception(ex)
    except Exception as ex:
        logging.error("Telemetry measurement reading failure: %s", str(ex))
        logging.exception(ex)


def sensor_log_writing_loop(start_time: float, runtime_limit: float, data_queue: Queue, output_directory: str):
    """Loop through clearing the data queue until RUNTIME_LIMIT has passed"""
    try:
        logging.info("Starting sensor log writing loop")
        last_queue_check = time.time()
        lines_written = 0
        with open(
            os.path.join(output_directory, f"sensor_log_{int(start_time)}.csv"), "w"
        ) as outfile:
            while True:
                try:
                    if not data_queue.empty():
                        row = data_queue.get()
                        if time.time() - start_time <= runtime_limit:
                            row_str = ",".join([str(p) for p in row])
                            logging.debug("Writing %s", row_str)
                            outfile.write(row_str + "\n")
                            lines_written += 1
                            if last_queue_check + 10.0 < time.time():
                                last_queue_check = time.time()
                                logging.info(
                                    f"Queue: {data_queue.qsize()} / Lines written: {lines_written} / {last_queue_check - start_time} seconds"
                                )
                            time.sleep(0)
                    else:
                        time.sleep(1)
                except Exception as ex:
                    logging.error("Telemetry log line writing failure: %s", str(ex))
                    logging.exception(ex)
        logging.info("Telemetry log writing loop complete")
    except Exception as ex:
        logging.error("Telemetry log writing failure: %s", str(ex))
        logging.exception(ex)


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
    except Exception as ex:
        logging.error("Video capture failure: %s", str(ex))
        logging.exception(ex)


def transmitter_thread(start_time: float, current_reading: AtomicValue):
    """Transmit the latest data"""
    try:
        rfm9x = init_radio(
            board.SCK_1, board.MOSI_1, board.MISO_1, board.D24, board.CE0
        )
        last_check = time.time()
        readings_sent = 0
        while True:
            info = current_reading.get_value()
            if info:
                is_all_floats = True
                for value in info:
                    if not isinstance(value, float):
                        is_all_floats = False
                        break
                if is_all_floats:
                    encoded = struct.pack("fffffffffffff", *info)
                    logging.debug(f"Transmitting {len(encoded)} bytes")
                    rfm9x.send(encoded)
                    readings_sent += 1
                    if last_check + 10.0 < time.time():
                        last_check = time.time()
                        logging.info(
                            f"Readings sent: {readings_sent} / {last_check - start_time} seconds"
                        )
                else:
                    logging.error(f"Bad info! ({info})")
            time.sleep(0)
    except Exception as ex:
        logging.error("Transmitter failure: %s", str(ex))
        logging.exception(ex)
