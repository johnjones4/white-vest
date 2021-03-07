"""Functions for the ground runtime"""
import logging
import struct
import time

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.const import TELEMETRY_STRUCT_STRING, TELEMETRY_TUPLE_LENGTH
from whitevest.lib.safe_buffer import SafeBuffer


def digest_next_ground_reading(
    rfm9x, buffer: SafeBuffer, gps_value: AtomicValue
) -> bool:
    """Read from the radio and the GPS and put the info in a queue"""
    packet = None
    start = time.time()
    while not packet and time.time() - start < 5:
        packet = rfm9x.receive()
        gps_info = gps_value.get_value()
    if not packet:
        info = [None] * TELEMETRY_TUPLE_LENGTH
        buffer.append((*info, None, *gps_info))
        return False
    info = struct.unpack(TELEMETRY_STRUCT_STRING, packet)
    logging.debug(info)
    buffer.append((*info, rfm9x.last_rssi, *gps_info))
    return True
