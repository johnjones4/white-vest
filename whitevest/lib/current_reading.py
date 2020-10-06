"""Thread-safe class for holding the most recent readings"""
from threading import Lock


class CurrentReading:
    """Thread-safe class for holding the most recent readings"""

    def __init__(self):
        """Initialize the class"""
        self.reading = None
        self.lock = Lock()

    def try_update(self, reading):
        """Try to update the latest reading without blocking"""
        if self.lock.acquire(False):
            self.reading = reading
            self.lock.release()

    def value(self):
        """Block until the latest reading is available"""
        with self.lock:
            return self.reading
