import sqlite3
import os.path as path
import os
import time
from whitevest.lib.safe_buffer import SafeBuffer
from whitevest.lib.atomic_value import AtomicValue
from threading import Lock
import csv

class BufferSessionStore:
    def __init__(self):
        self.buffer = SafeBuffer()
        self.current_session = AtomicValue()

    def initialize(self):
        self.connection = sqlite3.connect(path.join(os.getenv("DATA_DIRECTORY", "data"), "sessionstore.sqlite3"))
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS sessions (timestamp NUMBER UNIQUE NOT NULL)")
        self.connection.commit()
        self.create_new_session()

    def get_sessions(self):
        self.cursor.execute("SELECT timestamp FROM sessions WHERE timestamp != ? ORDER BY timestamp DESC", (self.current_session.get_value(), ))
        return [row[0] for row in self.cursor.fetchall()]

    def create_new_session(self):
        timestamp = int(time.time())
        self.current_session.update(timestamp)
        self.cursor.execute("INSERT INTO sessions (timestamp) VALUES (?)", (timestamp, ))
        self.connection.commit()
        self.buffer.purge()
        return timestamp

    def load_session(self, session):
        with open(self.data_path_for_session(session), "r") as csvfile:
            reader = csv.reader(csvfile)
            return [[float(v) for v in r] for r in reader]

    def data_path_for_session(self, session = None):
        if not session:
            session = self.current_session.get_value()
        return path.join(os.getenv("DATA_DIRECTORY", "data"), f"telemetry_log_{session}.csv")
