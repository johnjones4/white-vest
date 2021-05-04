"""Thread-safe class for holding a value"""
from threading import Lock


class AtomicValue:
    """Thread-safe class for holding a value"""

    def __init__(self, value=None):
        """Initialize the class"""
        self.value = value
        self.lock = Lock()

    def try_update(self, value):
        """Try to update the latest value without blocking"""
        if self.lock.acquire(False):  # pylint: disable=consider-using-with
            self.value = value
            self.lock.release()
            return True
        return False

    def update(self, value):
        """Block until we can write a value"""
        with self.lock:
            self.value = value

    def get_value(self):
        """Block until the latest value is available"""
        with self.lock:
            return self.value
