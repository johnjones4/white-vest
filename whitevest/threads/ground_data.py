"""Ground based telemetry reception and saving threads"""
import csv
import logging
import os
import struct
import time
from queue import Queue

import pynmea2

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.buffer_session_store import BufferSessionStore
from whitevest.lib.ground import digest_next_ground_reading
from whitevest.lib.utils import handle_exception, write_queue_log

if not os.getenv("REPLAY_DATA", False):
    import board

if not os.getenv("REPLAY_DATA", False):
    from whitevest.lib.hardware import init_radio


def telemetry_reception_loop(new_data_queue: Queue, gps_value: AtomicValue):
    """Loop forever reading telemetry and passing to the processing queue"""
    try:
        logging.info("Starting telemetry reading loop")
        rfm9x = init_radio(board.SCK, board.MOSI, board.MISO, board.CE1, board.D25)
        while True:
            try:
                digest_next_ground_reading(rfm9x, new_data_queue, gps_value)
                time.sleep(0)
            except Exception as ex:
                handle_exception("Telemetry point reading failure", ex)
    except Exception as ex:
        handle_exception("Telemetry point reading failure", ex)


def replay_telemetry(new_data_queue: Queue, replay_file: str):
    """Replays telemetry from a file"""
    try:
        while True:
            start_time = time.time()
            logging.info(f"Replaying telemetry from {replay_file}")
            with open(replay_file, "r") as file:
                reader = csv.reader(file)
                start_stamp = None
                for row in reader:
                    info = [float(v) for v in row]
                    if not start_stamp:
                        start_stamp = info[0]
                    while time.time() - start_time < info[0] - start_stamp:
                        pass
                    new_data_queue.put(info)
                    time.sleep(0)
    except Exception as ex:
        handle_exception("Telemetry replay failure", ex)


def telemetry_log_writing_loop(
    new_data_queue: Queue, buffer_session_store: BufferSessionStore
):
    """Loop forever clearing the data queue"""
    try:
        logging.info("Starting telemetry log writing loop")
        while not buffer_session_store.current_session.get_value():
            time.sleep(1)
        while True:
            start_time = buffer_session_store.current_session.get_value()
            with open(buffer_session_store.data_path_for_session(), "w") as outfile:
                while True:
                    try:
                        write_queue_log(outfile, new_data_queue, buffer_session_store)
                        time.sleep(0)
                        if (
                            start_time
                            != buffer_session_store.current_session.get_value()
                        ):
                            break
                    except Exception as ex:
                        handle_exception("Telemetry log line writing failure", ex)
    except Exception as ex:
        handle_exception("Telemetry log line writing failure", ex)
