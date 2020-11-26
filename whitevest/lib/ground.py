from queue import Queue
import logging
import struct

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.const import TELEMETRY_STRUCT_STRING


def digest_next_ground_reading(rfm9x, new_data_queue: Queue, gps_value: AtomicValue):
    """Read from the radio and the GPS and put the info in a queue"""
    packet = rfm9x.receive()
    if packet:
        info = struct.unpack(TELEMETRY_STRUCT_STRING, packet)
        logging.debug(info)
        gps_info = gps_value.get_value()
        new_data_queue.put((*info, rfm9x.last_rssi, *gps_info))
