"""Functions shared between air and ground runtimes"""
import logging
import struct
import time
from queue import Queue
from threading import Thread
from typing import Tuple

import pynmea2

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.configuration import Configuration
from whitevest.lib.const import TELEMETRY_STRUCT_STRING, TESTING_MODE

if not TESTING_MODE:
    from whitevest.lib.hardware import init_gps


def handle_exception(message: str, exception: Exception):
    """Log an exception"""
    logging.error(message)
    logging.exception(exception)


def write_queue_log(outfile, new_data_queue: Queue) -> int:
    """If there is data in the queue, write it to the file"""
    i = 0
    while not new_data_queue.empty():
        info = new_data_queue.get()
        row_str = ",".join([str(v) for v in info])
        logging.debug(row_str)
        outfile.write(row_str + "\n")
        i += 1
    return i


def take_gps_reading(sio, gps_value: AtomicValue) -> bool:
    """Grab the most recent data from GPS feed"""
    line = sio.readline()
    if line[0:6] == "$GPGGA":
        gps = pynmea2.parse(line)
        gps_value.update(
            (
                gps.latitude if gps else 0.0,
                gps.longitude if gps else 0.0,
                float(gps.gps_qual) if gps else 0.0,
                float(gps.num_sats) if gps else 0.0,
            )
        )
        return True
    return False


def gps_reception_loop(sio, gps_value: AtomicValue, continue_running: AtomicValue):
    """Loop forever reading GPS data and passing it to an atomic value"""
    if not sio:
        return
    while continue_running.get_value():
        try:
            take_gps_reading(sio, gps_value)
        except Exception as ex:  # pylint: disable=broad-except
            handle_exception("Telemetry reading failure", ex)
        time.sleep(0)


def create_gps_thread(
    configuration: Configuration, value: AtomicValue, continue_running: AtomicValue
):
    """Create a thread for tracking GPS"""
    return Thread(
        target=gps_reception_loop,
        args=(
            init_gps(configuration),
            value,
            continue_running,
        ),
        daemon=True,
    )


# pylint: disable=too-many-arguments
def digest_next_sensor_reading(
    start_time: float,
    data_queue: Queue,
    current_reading: AtomicValue,
    gps_value,
    altimeter_value,
    magnetometer_accelerometer_value,
) -> float:
    """Grab the latest values from all sensors and put the data in the queue and atomic store"""
    now = time.time()
    info = (
        now - start_time,
        *altimeter_value,
        *magnetometer_accelerometer_value,
        *gps_value,
    )
    data_queue.put(info)
    current_reading.try_update(info)
    return now


def write_sensor_log(
    start_time: float,
    outfile,
    data_queue: Queue,
    continue_running: AtomicValue,
    continue_logging: AtomicValue,
):
    """Write the queue to the log until told to stop"""
    lines_written = 0
    last_queue_check = time.time()
    while continue_running.get_value() and continue_logging.get_value():
        try:
            new_lines_written = write_queue_log(outfile, data_queue)
            if new_lines_written > 0:
                lines_written += new_lines_written
                if last_queue_check + 10.0 < time.time():
                    last_queue_check = time.time()
                    elapsed = last_queue_check - start_time
                    logging.info(
                        "Lines written: %d / %s seconds",
                        lines_written,
                        elapsed,
                    )
            time.sleep(5)
        except Exception as ex:  # pylint: disable=broad-except
            handle_exception("Telemetry log line writing failure", ex)


def transmit_latest_readings(
    pcnt_to_limit: AtomicValue,
    rfm9x,
    last_check: float,
    readings_sent: int,
    start_time: float,
    current_reading: AtomicValue,
) -> Tuple[int, float]:
    """Get the latest value from the sensor store and transmit it as a byte array"""
    info = current_reading.get_value()
    if info:
        clean_info = [float(i) for i in info]
        encoded = struct.pack(
            TELEMETRY_STRUCT_STRING, *(pcnt_to_limit.get_value(), *clean_info)
        )
        logging.debug("Transmitting %d bytes", len(encoded))
        rfm9x.send(encoded)
        readings_sent += 1
        if last_check > 0 and last_check + 10.0 < time.time():
            last_check = time.time()
            logging.info(
                "Readings sent: %d / %d seconds", readings_sent, last_check - start_time
            )
    return readings_sent, last_check
