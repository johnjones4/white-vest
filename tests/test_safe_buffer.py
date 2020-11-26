import random

from whitevest.lib.safe_buffer import SafeBuffer


def test_safe_buffer():
    buffer = SafeBuffer()
    vals = list()
    for _ in range(10):
        val = random.random()
        vals.append(val)
        buffer.append(val)
    assert buffer.size() == len(vals)
    print(buffer.get_range(4, 8))
    assert buffer.get_range(4, 8) == vals[4:8]
    buffer.purge()
    assert buffer.size() == 0
