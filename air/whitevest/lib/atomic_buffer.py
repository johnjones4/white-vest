"""A thread-safe buffer to hold values"""
from threading import Lock


class AtomicBuffer:
    """A thread-safe buffer to hold values"""

    def __init__(self, size: int = 0, default_value=None):
        self.default_value = default_value
        self.buffer = [default_value] * size
        self.pointer = 0
        self.lock = Lock()

    def put(self, value):
        with self.lock:
            self.buffer[self.pointer % len(self.buffer)] = value
            self.pointer += 1

    def read(self):
        with self.lock:
            output = [self.default_value] * len(self.buffer)
            for i, _ in enumerate(self.buffer):
                output[i] = self.buffer[(i + self.pointer) % len(self.buffer)]
            return output
