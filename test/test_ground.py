import random
from queue import Queue
import struct

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.const import TELEMETRY_TUPLE_LENGTH, TELEMETRY_STRUCT_STRING
from whitevest.lib.ground import digest_next_ground_reading


class MockRFM9x:
    def __init__(self, values):
        self.reading = struct.pack(TELEMETRY_STRUCT_STRING, *values)
        self.last_rssi = random.random()

    def receive(self):
        return self.reading

def test_digest_next_ground_reading():
    values = [random.random() for _ in range(TELEMETRY_TUPLE_LENGTH)]
    rfm9x = MockRFM9x(values)
    new_data_queue = Queue()
    gps_value = AtomicValue([random.random() for _ in range(4)])
    digest_next_ground_reading(rfm9x, new_data_queue, gps_value)
    assert new_data_queue.qsize() == 1
    expected = (
        *values,
        rfm9x.last_rssi,
        *gps_value.get_value()
    )
    assert new_data_queue.get() == expected
