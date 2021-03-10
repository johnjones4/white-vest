"""Thread-safe buffer to store received telemetry"""
import logging
from threading import Lock


class SafeBuffer:
    """Thread-safe buffer to store received telemetry"""

    def __init__(self):
        """Initialize the buffer"""
        self.data_buffer = list()
        self.lock = Lock()

    def append(self, reading):
        """Append new data"""
        with self.lock:
            self.data_buffer.append(reading)

    def get_range(self, start, end):
        """Get a specific range of data from the buffer"""
        logging.debug("Sending %d to %d", start, end)
        # pylint: disable=chained-comparison
        with self.lock:
            if (
                start >= 0
                and start <= len(self.data_buffer)
                and end >= 0
                and end <= len(self.data_buffer)
            ):
                return self.data_buffer[start:end]
        return []

    def size(self):
        """Get the buffer size"""
        with self.lock:
            return len(self.data_buffer)

    def purge(self):
        """Empty the buffer"""
        with self.lock:
            self.data_buffer = list()
