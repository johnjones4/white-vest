import io
import random
import time
from queue import Queue
from threading import Thread

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.atomic_buffer import AtomicBuffer
from whitevest.lib.configuration import Configuration
from whitevest.lib.const import TELEMETRY_TUPLE_LENGTH
from whitevest.lib.utils import (
    digest_next_sensor_reading,
    take_gps_reading,
    transmit_latest_readings,
    write_queue_log,
    write_sensor_log,
)


class MockSerial:
    def __init__(self, line):
        self.line = line

    def readline(self):
        return self.line


def test_write_queue_log():
    outfile = io.StringIO("")
    data_queue = Queue()
    configuration = Configuration(None, dict(output_directory="./data"))
    while data_queue.qsize() < 10:
        data_queue.put((random.random(), random.random(), random.random()))
    write_queue_log(outfile, data_queue)
    contents = outfile.getvalue()
    assert contents
    assert len(contents.split("\n")) == 11


def test_take_gps_reading():
    line = f"$GPGGA,134658.00,5106.9792,N,11402.3003,W,2,09,1.0,1048.47,M,-16.27,M,08,AAAA*60"
    sio = MockSerial(line)
    val = AtomicValue()
    take_gps_reading(sio, val)
    assert val.get_value() == (51.11632, -114.03833833333333, 2, 9)


class MockRFM9X:
    def send(self, value):
        self.sent = value


def test_digest_next_sensor_reading():
    start_time = time.time()
    altimeter_value = [random.random() for _ in range(2)]
    gps_value = [random.random() for _ in range(4)]
    magnetometer_accelerometer_value = [random.random() for _ in range(6)]
    data_queue = Queue()
    current_reading = AtomicBuffer(1)
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
        *altimeter_value,
        *magnetometer_accelerometer_value,
        *gps_value,
    )
    assert logged
    assert logged == expected_tuple
    assert current_reading.read()[0] == expected_tuple
    assert len(logged) == TELEMETRY_TUPLE_LENGTH


def test_write_sensor_log():
    start_time = time.time()
    outfile = io.StringIO("")
    data_queue = Queue()
    while data_queue.qsize() < 100:
        data_queue.put((random.random(), random.random(), random.random()))
    continue_running = AtomicValue(True)
    thread = Thread(
        target=write_sensor_log,
        args=(start_time, outfile, data_queue, continue_running, continue_running),
    )
    thread.start()
    time.sleep(5)
    continue_running.update(False)
    thread.join()
    contents = outfile.getvalue()
    assert contents
    assert len(contents.split("\n")) > 0


def test_transmit_latest_readings():
    last_check = 1
    readings_sent = 0
    start_time = time.time()
    rfm9x = MockRFM9X()
    camera_is_running = AtomicValue(0.0)
    current_reading = AtomicBuffer(2)
    current_reading.put([random.random() for _ in range(TELEMETRY_TUPLE_LENGTH)])
    current_reading.put([random.random() for _ in range(TELEMETRY_TUPLE_LENGTH)])
    readings_sent_1, last_check_1 = transmit_latest_readings(
        camera_is_running, rfm9x, last_check, readings_sent, start_time, current_reading
    )
    assert readings_sent_1 > readings_sent
    assert last_check < last_check_1
    assert last_check_1 <= time.time()
    assert len(rfm9x.sent) == (TELEMETRY_TUPLE_LENGTH * 8 * 2) + 8
