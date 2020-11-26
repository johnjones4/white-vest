import logging
from queue import Queue
import time
import pynmea2

from whitevest.lib.buffer_session_store import BufferSessionStore
from whitevest.lib.atomic_value import AtomicValue


def handle_exception(message: str, exception: Exception):
    """Log an exception"""
    logging.error(message)
    logging.exception(exception)


def write_queue_log(
    outfile, new_data_queue: Queue, buffer_session_store: BufferSessionStore
):
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


def take_gps_reading(sio, gps_value: AtomicValue):
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


def gps_reception_loop(sio, gps_value: AtomicValue):
    """Loop forever reading GPS data and passing it to an atomic value"""
    while True:
        try:
            take_gps_reading(sio, gps_value)
        except Exception as ex:
            handle_exception("Telemetry reading failure", ex)
        time.sleep(0)
