"""Data capture session storage engine"""
import csv
import os.path as path
import sqlite3
import time
from typing import List

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.safe_buffer import SafeBuffer


class BufferSessionStore:
    """Data capture session storage engine"""

    def __init__(self, output_dir: str, sql_file: str = "sessionstore.sqlite3"):
        """Create a new session store"""
        self.buffer = SafeBuffer()
        self.current_session = AtomicValue()
        self.output_dir = output_dir
        self.sql_file = sql_file
        self.connection = None
        self.cursor = None

    def initialize(self):
        """Initialize the store. (Pins the SQLite connection to the calling thread)"""
        self.connection = sqlite3.connect(path.join(self.output_dir, self.sql_file))
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS sessions (timestamp NUMBER UNIQUE NOT NULL)"
        )
        self.connection.commit()
        self.create_new_session()

    def get_sessions(self) -> List[float]:
        """Get a list of saved sessions"""
        self.cursor.execute(
            "SELECT timestamp FROM sessions WHERE timestamp != ? ORDER BY timestamp DESC",
            (self.current_session.get_value(),),
        )
        return [row[0] for row in self.cursor.fetchall()]

    def create_new_session(self) -> float:
        """Create and save a new session"""
        timestamp = int(time.time())
        self.current_session.update(timestamp)
        self.cursor.execute("INSERT INTO sessions (timestamp) VALUES (?)", (timestamp,))
        self.connection.commit()
        self.buffer.purge()
        return timestamp

    def load_session(self, session) -> List[List[float]]:
        """Load data from a given session"""
        with open(self.data_path_for_session(session), "r") as csvfile:
            reader = csv.reader(csvfile)
            return [[float(v) for v in r] for r in reader]

    def data_path_for_session(self, session=None) -> str:
        """Get the path to the given session's data"""
        if not session:
            session = self.current_session.get_value()
        return path.join(self.output_dir, f"telemetry_log_{session}.csv")
