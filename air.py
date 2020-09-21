"""Inboard data capture and transmission script"""
import logging
import os
import os.path
import struct
import time
from queue import Queue
from threading import Lock, Thread

import adafruit_bmp3xx
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
import adafruit_rfm9x
import board
import busio
import digitalio
import picamera
from digitalio import DigitalInOut


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


def init_radio():
    """Initialize the radio"""
    logging.info("Initializing transmitter")
    spi = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)
    cs = DigitalInOut(board.D24)
    reset = DigitalInOut(board.CE0)
    rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0, baudrate=1000000)
    rfm9x.tx_power = 23
    return rfm9x


def init_altimeter():
    """Initialize the sensor for pressure, temperature, and altitude"""
    logging.info("Initializing altimeter")
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    cs = digitalio.DigitalInOut(board.D5)
    bmp = adafruit_bmp3xx.BMP3XX_SPI(spi, cs)
    bmp.sea_level_pressure = float(os.getenv("PRESSURE_AT_SEA_LEVEL", 1013.25))
    return bmp


def init_magnetometer_accelerometer():
    """Initialize the sensor for magnetic and acceleration"""
    i2c = busio.I2C(board.SCL, board.SDA)
    mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
    accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
    return mag, accel


def sensor_reading_loop(start_time, current_reading, data_queue):
    """Read from the sensors on and infinite loop and queue it for transmission and logging"""
    try:
        logging.info("Starting sensor measurement loop")
        bmp = init_altimeter()
        mag, accel = init_magnetometer_accelerometer()
        while True:
            try:
                altitude = bmp.altitude
                temperature = bmp.temperature
                pressure = bmp.pressure
                (acceleration_x, acceleration_y, acceleration_z) = accel.acceleration
                (magnetic_x, magnetic_y, magnetic_z) = mag.magnetic
                info = (
                    time.time() - start_time,
                    pressure,
                    temperature,
                    altitude,
                    acceleration_x,
                    acceleration_y,
                    acceleration_z,
                    magnetic_x,
                    magnetic_y,
                    magnetic_z,
                )
                logging.debug("Read (At %f) %f %f %f %f %f %f %f %f %f", *info)
                data_queue.put(info)
                current_reading.try_update(info)
                time.sleep(0)
            except Exception as ex:
                logging.error(
                    "Telemetry measurement point reading failure: %s", str(ex)
                )
                logging.exception(ex)
    except Exception as ex:
        logging.error("Telemetry measurement reading failure: %s", str(ex))
        logging.exception(ex)


def sensor_log_writing_loop(start_time, runtime_limit, data_queue, output_directory):
    """Loop through clearing the data queue until RUNTIME_LIMIT has passed"""
    try:
        logging.info("Starting sensor log writing loop")
        last_queue_check = time.time()
        lines_written = 0
        with open(
            os.path.join(output_directory, f"sensor_log_{int(start_time)}.csv"), "w"
        ) as outfile:
            while time.time() - start_time <= runtime_limit:
                try:
                    if not data_queue.empty():
                        row = data_queue.get()
                        row_str = ",".join([str(p) for p in row])
                        logging.debug("Writing %s", row_str)
                        outfile.write(row_str + "\n")
                        lines_written += 1
                        if last_queue_check + 10.0 < time.time():
                            last_queue_check = time.time()
                            logging.info(
                                f"Queue: {data_queue.qsize()} / Lines written: {lines_written} / {last_queue_check - start_time} seconds"
                            )
                        time.sleep(0)
                    else:
                        time.sleep(1)
                except Exception as ex:
                    logging.error("Telemetry log line writing failure: %s", str(ex))
                    logging.exception(ex)
        logging.info("Telemetry log writing loop complete")
    except Exception as ex:
        logging.error("Telemetry log writing failure: %s", str(ex))
        logging.exception(ex)


def camera_thread(start_time, runtime_limit, output_directory):
    """Start the camera and log the video"""
    try:
        logging.info("Starting video capture")
        camera = picamera.PiCamera(framerate=90)
        camera.start_recording(
            os.path.join(output_directory, f"video_{int(start_time)}.h264")
        )
        camera.wait_recording(runtime_limit)
        camera.stop_recording()
        logging.info("Video capture complete")
    except Exception as ex:
        logging.error("Video capture failure: %s", str(ex))
        logging.exception(ex)


def transmitter_thread(start_time, current_reading):
    """Transmit the latest data"""
    try:
        rfm9x = init_radio()
        last_check = time.time()
        readings_sent = 0
        while True:
            info = current_reading.value()
            if info:
                is_all_floats = True
                for value in info:
                    if not isinstance(value, float):
                        is_all_floats = False
                        break
                if is_all_floats:
                    encoded = struct.pack("ffffffffff", *info)
                    logging.debug(f"Transmitting {len(encoded)} bytes")
                    rfm9x.send(encoded)
                    readings_sent += 1
                    if last_check + 10.0 < time.time():
                        last_check = time.time()
                        logging.info(
                            f"Readings sent: {readings_sent} / {last_check - start_time} seconds"
                        )
                else:
                    logging.error(f"Bad info! ({info})")
            time.sleep(0)
    except Exception as ex:
        logging.error("Transmitter failure: %s", str(ex))
        logging.exception(ex)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    # How long should logging and recording run
    RUNTIME_LIMIT = int(os.getenv("RUNTIME_LIMIT", 600))

    # Path to where to save data
    OUTPUT_DIRECTORY = os.getenv("OUTPUT_DIRECTORY", "./data")

    # Queue to manage data synchronization between sensor reading, transmission, and data logging
    DATA_QUEUE = Queue()

    # Timestamp to use for log files and log saving cutoff
    START_TIME = time.time()

    # Thread safe place to store altitude reading
    CURRENT_READING = CurrentReading()

    WRITE_THREAD = Thread(
        target=sensor_log_writing_loop,
        args=(START_TIME, RUNTIME_LIMIT, DATA_QUEUE, OUTPUT_DIRECTORY),
        daemon=True,
    )
    WRITE_THREAD.start()

    CAMERA_THREAD = Thread(
        target=camera_thread,
        args=(START_TIME, RUNTIME_LIMIT, OUTPUT_DIRECTORY),
        daemon=True,
    )
    CAMERA_THREAD.start()

    TRANSMITTER_THREAD = Thread(
        target=transmitter_thread,
        args=(
            START_TIME,
            CURRENT_READING,
        ),
        daemon=True,
    )
    TRANSMITTER_THREAD.start()

    sensor_reading_loop(START_TIME, CURRENT_READING, DATA_QUEUE)
