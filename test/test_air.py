import io
import random
import time
from queue import Queue

from whitevest.lib.air import (
    digest_next_sensor_reading,
    transmit_latest_readings,
    write_sensor_log,
)
from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.const import TELEMETRY_TUPLE_LENGTH


class MockBMP:
    def __init__(self):
        self.temperature = random.random()
        self.pressure = random.random()

    def _read(self):
        return self.temperature, self.pressure


class MockAcceleration:
    def __init__(self):
        self.acceleration = (random.random(), random.random(), random.random())


class MockMagnetic:
    def __init__(self):
        self.magnetic = (random.random(), random.random(), random.random())


class MockRFM9X:
    def send(self, value):
        self.sent = value


def test_digest_next_sensor_reading():
    start_time = time.time()
    bmp = MockBMP()
    gps_value = AtomicValue([random.random() for _ in range(4)])
    accel = MockAcceleration()
    mag = MockMagnetic()
    data_queue = Queue()
    current_reading = AtomicValue()
    now = digest_next_sensor_reading(
        start_time, bmp, gps_value, accel, mag, data_queue, current_reading
    )
    logged = data_queue.get()
    expected_tuple = (
        now - start_time,
        *bmp._read(),
        *accel.acceleration,
        *mag.magnetic,
        *gps_value.get_value(),
    )
    assert logged
    assert logged == expected_tuple
    assert current_reading.get_value() == expected_tuple
    assert len(logged) == TELEMETRY_TUPLE_LENGTH


def test_write_sensor_log():
    start_time = time.time()
    runtime_limit = 1
    outfile = io.StringIO("")
    data_queue = Queue()
    while data_queue.qsize() < 100000:
        data_queue.put((random.random(), random.random(), random.random()))
    write_sensor_log(start_time, runtime_limit, outfile, data_queue)
    contents = outfile.getvalue()
    assert time.time() >= start_time + runtime_limit
    assert contents
    assert len(contents.split("\n")) <= 100000


def test_transmit_latest_readings():
    last_check = 0
    readings_sent = 0
    start_time = time.time()
    rfm9x = MockRFM9X()
    current_reading = AtomicValue(
        [random.random() for _ in range(TELEMETRY_TUPLE_LENGTH)]
    )
    readings_sent_1, last_check_1 = transmit_latest_readings(
        rfm9x, last_check, readings_sent, start_time, current_reading
    )
    assert readings_sent_1 > readings_sent
    assert last_check < last_check_1
    assert last_check_1 <= time.time()
    assert len(rfm9x.sent) == (TELEMETRY_TUPLE_LENGTH * 8)
