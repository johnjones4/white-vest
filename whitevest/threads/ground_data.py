"""Ground based telemetry reception and saving threads"""
import csv
import logging
import time

from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.configuration import Configuration
from whitevest.lib.const import TESTING_MODE
from whitevest.lib.ground import digest_next_ground_reading
from whitevest.lib.safe_buffer import SafeBuffer
from whitevest.lib.utils import handle_exception

if not TESTING_MODE:
    from whitevest.lib.hardware import init_radio


def telemetry_reception_loop(
    configuration: Configuration, buffer: SafeBuffer, gps_value: AtomicValue
):
    """Loop forever reading telemetry and passing to the processing queue"""
    try:
        logging.info("Starting telemetry reading loop")
        rfm9x = init_radio(configuration)
        if not rfm9x:
            return
        while True:
            try:
                if digest_next_ground_reading(rfm9x, buffer, gps_value):
                    time.sleep(0)
                else:
                    time.sleep(1)
            except Exception as ex:  # pylint: disable=broad-except
                handle_exception("Telemetry point reading failure", ex)
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Telemetry point reading failure", ex)


def replay_telemetry(buffer: SafeBuffer, replay_file: str):
    """Replays telemetry from a file"""
    try:
        while True:
            start_time = time.time()
            logging.info("Replaying telemetry from %d", replay_file)
            with open(replay_file, "r") as file:
                reader = csv.reader(file)
                start_stamp = None
                for row in reader:
                    info = [float(v) for v in row]
                    if not start_stamp:
                        start_stamp = info[0]
                    while time.time() - start_time < info[0] - start_stamp:
                        pass
                    buffer.append(info)
                    time.sleep(0)
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("Telemetry replay failure", ex)
