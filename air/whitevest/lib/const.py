"""Shared constants for the runtimes"""
import os

TELEMETRY_TUPLE_LENGTH = 13
TELEMETRY_STRUCT_STRING = "".join(["d" for _ in range(TELEMETRY_TUPLE_LENGTH)])

TESTING_MODE = os.getenv("REPLAY_DATA") or os.getenv("TESTING")
