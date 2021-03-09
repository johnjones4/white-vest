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


class MockRFM9X:
    def send(self, value):
        self.sent = value


def test_digest_next_sensor_reading():
    start_time = time.time()
    altimeter_value = AtomicValue([random.random() for _ in range(2)])
    gps_value = AtomicValue([random.random() for _ in range(4)])
    magnetometer_accelerometer_value = AtomicValue([random.random() for _ in range(6)])
    data_queue = Queue()
    current_reading = AtomicValue()
    now = digest_next_sensor_reading(
        start_time,
        data_queue,
        current_reading,
        gps_value,
        altimeter_value,
        magnetometer_accelerometer_value,
    )
    logged = data_queue.get()
    expected_tuple = (
        now - start_time,
        *altimeter_value.get_value(),
        *magnetometer_accelerometer_value.get_value(),
        *gps_value.get_value(),
    )
    assert logged
    assert logged == expected_tuple
    assert current_reading.get_value() == expected_tuple
    assert len(logged) == TELEMETRY_TUPLE_LENGTH


def test_write_sensor_log():
    start_time = time.time()
    runtime_limit = 5
    outfile = io.StringIO("")
    data_queue = Queue()
    while data_queue.qsize() < 100:
        data_queue.put((random.random(), random.random(), random.random()))
    write_sensor_log(start_time, runtime_limit, outfile, data_queue)
    contents = outfile.getvalue()
    assert time.time() >= start_time + runtime_limit
    assert contents
    assert len(contents.split("\n")) > 0


def test_transmit_latest_readings():
    last_check = 1
    readings_sent = 0
    start_time = time.time()
    rfm9x = MockRFM9X()
    camera_is_running = AtomicValue(0.0)
    current_reading = AtomicValue(
        [random.random() for _ in range(TELEMETRY_TUPLE_LENGTH - 1)]
    )
    readings_sent_1, last_check_1 = transmit_latest_readings(
        camera_is_running, rfm9x, last_check, readings_sent, start_time, current_reading
    )
    assert readings_sent_1 > readings_sent
    assert last_check < last_check_1
    assert last_check_1 <= time.time()
    assert len(rfm9x.sent) == (TELEMETRY_TUPLE_LENGTH * 8)
