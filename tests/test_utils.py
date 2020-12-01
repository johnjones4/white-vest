import io
import random
from queue import Queue

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.buffer_session_store import BufferSessionStore
from whitevest.lib.utils import take_gps_reading, write_queue_log
from whitevest.lib.configuration import Configuration


class MockSerial:
    def __init__(self, line):
        self.line = line

    def readline(self):
        return self.line


def test_write_queue_log():
    outfile = io.StringIO("")
    data_queue = Queue()
    configuration = Configuration(None, dict(
        output_directory="./data"
    ))
    buffer_store = BufferSessionStore(configuration)
    while data_queue.qsize() < 10:
        data_queue.put((random.random(), random.random(), random.random()))
    write_queue_log(outfile, data_queue, buffer_store)
    assert buffer_store.buffer.size() == 1
    contents = outfile.getvalue()
    assert contents
    assert len(contents.split("\n")) == 2


def test_take_gps_reading():
    line = f"$GPGGA,134658.00,5106.9792,N,11402.3003,W,2,09,1.0,1048.47,M,-16.27,M,08,AAAA*60"
    sio = MockSerial(line)
    val = AtomicValue()
    take_gps_reading(sio, val)
    assert val.get_value() == (51.11632, -114.03833833333333, 2, 9)
