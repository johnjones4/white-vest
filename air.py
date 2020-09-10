"""Inboard data capture and transmission script"""
import time
import board
import busio
import adafruit_bmp3xx
import digitalio
import os
from rpi_rf import RFDevice
import logging
from threading import Thread
import picamera
from collections import Queue
import adafruit_lsm303_accel
import adafruit_lis2mdl

# Queue to manage data synchronization between sensor reading, transmission, and data logging
DATA_QUEUE = Queue()
# Timestamp to use for log files and log saving cutoff
START_TIME = time.time()


def init_altimeter():
    """Initialize the sensor for pressure, temperature, and altitude"""
    logging.info("Initializing altimeter")
    SPI = busio.SPI(board.SCK, board.MOSI, board.MISO)
    CS = digitalio.DigitalInOut(board.D5)
    bmp = adafruit_bmp3xx.BMP3XX_SPI(SPI, CS)
    bmp.sea_level_pressure = float(os.getenv("PRESSURE_AT_SEA_LEVEL", 1013.25))
    return bmp


def init_magnetometer_accelerometer():
    """Initialize the sensor for magnetic and acceleration"""
    i2c = busio.I2C(board.SCL, board.SDA)
    mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
    accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
    return mag, accel


def init_transmitter():
    """Initialize the data transmitter"""
    logging.info("Initializing transmitter")
    tx = RFDevice(17)
    tx.enable_tx()
    return tx


def sensor_reading_loop(data_queue):
    """Read from the sensors every 10th of a second on infinite loop, transmit the altitude, and queue the rest for logging"""
    try:
        logging.info("Starting sensor measurement loop")
        bmp = init_altimeter()
        mag, accel = init_magnetometer_accelerometer()
        tx = init_transmitter()
        while True:
            try:
                now = time.time()
                altitude = bmp.altitude
                temperature = bmp.temperature
                pressure = bmp.pressure
                (acceleration_x, acceleration_y, acceleration_z) = accel.acceleration
                (magnetic_x, magnetic_y, magnetic_z) = mag.magnetic
                logging.debug("Read %f %f %f %f %f %f %f %f %f", 
                    pressure,
                    temperature,
                    altitude,
                    acceleration_x,
                    acceleration_y,
                    acceleration_z,
                    magnetic_x,
                    magnetic_y,
                    magnetic_z
                )
                data_queue.put((
                    now,
                    pressure,
                    temperature,
                    altitude,
                    acceleration_x,
                    acceleration_y,
                    acceleration_z,
                    magnetic_x,
                    magnetic_y,
                    magnetic_z
                ))
                tx.tx_code(altitude)
                time.sleep(0.1)
            except Exception as ex:
                logging.error("Telemetry measurement point reading failure: %s", str(ex))
                logging.exception(ex)
    except Exception as ex:
        logging.error("Telemetry measurement reading failure: %s", str(ex))
        logging.exception(ex)


def write_sensor_buffer(start_time, data_queue):
    """Write all queued data to the log"""
    try:
        with open(f"data/sensor_log_{int(start_time)}.csv", "a") as outfile:
            while not data_queue.empty():
                try:
                    row = data_queue.get()
                    row_str = ",".join([str(p) in p for row])
                    logging.debug("Writing %s", row_str)
                    outfile.write(row_str + "\n")
                    time.sleep(0)
                except Exception as ex:
                    logging.error("Telemetry log line writing failure: %s", str(ex))
                    logging.exception(ex)
        time.sleep(1)
    except Exception as ex:
        logging.error("Telemetry log output writing failure: %s", str(ex))
        logging.exception(ex)


def sensor_log_writing_loop(start_time, data_queue):
    """Loop through clearing the data queue until RUNTIME_LIMIT has passed"""
    try:
        logging.info("Starting sensor log writing loop")
        limit = runtime_limit()
        while start_time - time.time() > limit:
            write_sensor_buffer(start_time, data_queue)
        write_sensor_buffer(start_time, data_queue)
        logging.info("Telemetry log writing loop complete")
    except Exception as ex:
        logging.error("Telemetry log writing failure: %s", str(ex))
        logging.exception(ex)


def camera_thread(start_time):
    """Start the camera and log the video"""
    try:
        logging.info("Starting video capture")
        camera = picamera.PiCamera()
        camera.start_preview()
        camera.start_recording(f"data/video_{int(start_time)}.mov")
        sleep(runtime_limit())
        camera.stop_recording()
        camera.stop_preview()
        logging.info("Video capture complete")
    except Exception as ex:
        logging.error("Video capture failure: %s", str(ex))
        logging.exception(ex)


def runtime_limit():
    """Helper to get RUNTIME_LIMIT"""
    return int(os.getenv("RUNTIME_LIMIT", 1800))


if __name__ == "__main__":
    WRITE_THREAD = Thread(target=sensor_log_writing_loop, args=(START_TIME, DATA_QUEUE,), daemon=True)
    WRITE_THREAD.start()

    CAMERA_THREAD = Thread(target=camera_thread, args=(START_TIME,), daemon=True)
    CAMERA_THREAD.start()

    sensor_reading_loop(DATA_QUEUE)
