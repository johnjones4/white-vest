import logging
import struct
import time
from queue import Queue

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.const import TELEMETRY_STRUCT_STRING
from whitevest.lib.utils import handle_exception, write_queue_log


def digest_next_sensor_reading(
    start_time: float,
    bmp,
    gps_value: AtomicValue,
    accel,
    mag,
    data_queue: Queue,
    current_reading: AtomicValue,
):
    """Grab the latest values from all sensors and put the data in the queue and atomic store"""
    now = time.time()
    info = (
        now - start_time,
        *bmp._read(),
        *accel.acceleration,
        *mag.magnetic,
        *gps_value.get_value(),
    )
    data_queue.put(info)
    current_reading.try_update(info)
    return now


def write_sensor_log(
    start_time: float, runtime_limit: float, outfile, data_queue: Queue
):
    """Write the queue to the log for a specified period"""
    lines_written = 0
    last_queue_check = time.time()
    while time.time() - start_time <= runtime_limit:
        try:
            if write_queue_log(outfile, data_queue, None):
                lines_written += 1
                if last_queue_check + 10.0 < time.time():
                    last_queue_check = time.time()
                    logging.info(
                        f"Queue: {data_queue.qsize()} / Lines written: {lines_written} / {last_queue_check - start_time} seconds"
                    )
            time.sleep(0)
        except Exception as ex:
            handle_exception("Telemetry log line writing failure", ex)


def transmit_latest_readings(
    rfm9x,
    last_check: float,
    readings_sent: float,
    start_time: float,
    current_reading: AtomicValue,
):
    """Get the latest value from the sensor store and transmit it as a byte array"""
    info = current_reading.get_value()
    if info:
        clean_info = [float(i) for i in info]
        encoded = struct.pack(TELEMETRY_STRUCT_STRING, *clean_info)
        logging.debug(f"Transmitting {len(encoded)} bytes")
        rfm9x.send(encoded)
        readings_sent += 1
        if last_check + 10.0 < time.time():
            last_check = time.time()
            logging.info(
                f"Readings sent: {readings_sent} / {last_check - start_time} seconds"
            )
    return readings_sent, last_check
