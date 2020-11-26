import random
from whitevest.lib.atomic_value import AtomicValue

def test_atomic_value():
    raw_value = random.random()
    value = AtomicValue(raw_value)
    assert raw_value == value.get_value()
    value.update(random.random())
    assert raw_value != value.get_value()

def test_atomic_value_try_update_succeed():
    raw_value = random.random()
    value = AtomicValue(raw_value)
    value.lock.acquire()
    value.lock.release()
    assert value.try_update(random.random())
    assert raw_value != value.get_value()


def test_atomic_value_try_update_fail():
    raw_value = random.random()
    value = AtomicValue(raw_value)
    value.lock.acquire()
    assert not value.try_update(random.random())
    value.lock.release()
    assert raw_value == value.get_value()
