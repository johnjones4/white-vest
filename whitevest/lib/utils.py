"""Functions shared between air and ground runtimes"""
import logging
import time
from queue import Queue
from threading import Thread

import pynmea2

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.buffer_session_store import BufferSessionStore
from whitevest.lib.configuration import Configuration
from whitevest.lib.const import TESTING_MODE

if not TESTING_MODE:
    from whitevest.lib.hardware import init_gps


def handle_exception(message: str, exception: Exception):
    """Log an exception"""
    logging.error(message)
    logging.exception(exception)


def write_queue_log(
    outfile, new_data_queue: Queue, buffer_session_store: BufferSessionStore
) -> bool:
    """If there is data in the queue, write it to the file"""
    if not new_data_queue.empty():
        info = new_data_queue.get()
        row_str = ",".join([str(v) for v in info])
        logging.debug(row_str)
        outfile.write(row_str + "\n")
        if buffer_session_store:
            buffer_session_store.buffer.append(info)
        return True
    return False


def take_gps_reading(sio, gps_value: AtomicValue) -> bool:
    """Grab the most recent data from GPS feed"""
    line = sio.readline()
    if line[0:6] == "$GPGGA":
        gps = pynmea2.parse(line)
        gps_value.update(
            (
                gps.latitude if gps else 0.0,
                gps.longitude if gps else 0.0,
                gps.gps_qual if gps else 0.0,
                float(gps.num_sats) if gps else 0.0,
            )
        )
        return True
    return False


def gps_reception_loop(sio, gps_value: AtomicValue):
    """Loop forever reading GPS data and passing it to an atomic value"""
    if not sio:
        return
    while True:
        try:
            take_gps_reading(sio, gps_value)
        except Exception as ex:  # pylint: disable=broad-except
            handle_exception("Telemetry reading failure", ex)
        time.sleep(0)


def create_gps_thread(configuration: Configuration, value: AtomicValue):
    """Create a thread for tracking GPS"""
    return Thread(
        target=gps_reception_loop,
        args=(
            init_gps(configuration),
            value,
        ),
        daemon=True,
    )
