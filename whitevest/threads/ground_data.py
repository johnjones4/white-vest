"""Ground based telemetry reception and saving threads"""
import csv
import logging
import struct
import time
import os

if not os.getenv("REPLAY_DATA", False):
    import board

if not os.getenv("REPLAY_DATA", False):
    from whitevest.lib.hardware import init_radio


def telemetry_reception_loop(new_data_queue):
    """Loop forever reading telemetry and passing to the processing queue"""
    try:
        logging.info("Starting telemetry reading loop")
        rfm9x = init_radio(board.SCK, board.MOSI, board.MISO, board.CE1, board.D25)
        while True:
            try:
                packet = rfm9x.receive()
                if packet:
                    info = struct.unpack("fffffffff", packet)
                    logging.debug(info)
                    new_data_queue.put((*info, rfm9x.last_rssi))
                time.sleep(0)
            except Exception as ex:
                logging.error("Telemetry point reading failure: %s", str(ex))
                logging.exception(ex)
    except Exception as ex:
        logging.error("Telemetry reading failure: %s", str(ex))
        logging.exception(ex)


def replay_telemetry(new_data_queue, replay_file):
    """Replays telemetry from a file"""
    try:
        while True:
            start_time = time.time()
            logging.info(f"Replaying telemetry from {replay_file}")
            with open(replay_file, "r") as file:
                reader = csv.reader(file)
                start_stamp = None
                for row in reader:
                    info = (*[float(v) for v in row], 38.804836, -77.046921, 38.8040, -77.0480)
                    # info = [float(v) for v in row]
                    if not start_stamp:
                        start_stamp = info[0]
                    while time.time() - start_time < info[0] - start_stamp:
                        pass
                    new_data_queue.put(info)
                    time.sleep(0)
    except Exception as ex:
        logging.error("Telemetry replay failure: %s", str(ex))
        logging.exception(ex)


def telemetry_log_writing_loop(new_data_queue, buffer_session_store):
    """Loop forever clearing the data queue"""
    try:
        logging.info("Starting telemetry log writing loop")
        while True:
            while not buffer_session_store.current_session.get_value():
                time.sleep(1)
            start_time = buffer_session_store.current_session.get_value()
            with open(buffer_session_store.data_path_for_session(), "w") as outfile:
                while True:
                    try:
                        if not new_data_queue.empty():
                            info = new_data_queue.get()
                            buffer_session_store.buffer.append(info)
                            row_str = ",".join([str(v) for v in info])
                            logging.debug(row_str)
                            outfile.write(row_str + "\n")
                        time.sleep(0)
                        if start_time != buffer_session_store.current_session.get_value():
                            break
                    except Exception as ex:
                        logging.error("Telemetry log line writing failure: %s", str(ex))
                        logging.exception(ex)
    except Exception as ex:
        logging.error("Telemetry log writing failure: %s", str(ex))
        logging.exception(ex)


