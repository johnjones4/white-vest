import random
import struct

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.const import TELEMETRY_STRUCT_STRING, TELEMETRY_TUPLE_LENGTH
from whitevest.lib.ground import digest_next_ground_reading
from whitevest.lib.safe_buffer import SafeBuffer


class MockRFM9x:
    def __init__(self, values):
        if values:
            self.reading = struct.pack(TELEMETRY_STRUCT_STRING, *values)
            self.last_rssi = random.random()
        else:
            self.reading = None

    def receive(self):
        return self.reading


def test_digest_next_ground_reading_1():
    values = [random.random() for _ in range(TELEMETRY_TUPLE_LENGTH)]
    rfm9x = MockRFM9x(values)
    buffer = SafeBuffer()
    gps_value = AtomicValue([random.random() for _ in range(4)])
    assert digest_next_ground_reading(rfm9x, buffer, gps_value)
    assert buffer.size() == 1
    expected = (*values, rfm9x.last_rssi, *gps_value.get_value())
    assert buffer.get_range(0,1)[0] == expected


def test_digest_next_ground_reading_2():
    rfm9x = MockRFM9x(None)
    buffer = SafeBuffer()
    gps_value = AtomicValue([random.random() for _ in range(4)])
    assert not digest_next_ground_reading(rfm9x, buffer, gps_value)
    assert buffer.size() == 1
    values = [None] * TELEMETRY_TUPLE_LENGTH
    expected = (*values, None, *gps_value.get_value())
    assert buffer.get_range(0,1)[0] == expected
