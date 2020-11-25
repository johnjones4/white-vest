"""Utils for setting up hardware access"""
import logging

import adafruit_bmp3xx
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
import adafruit_rfm9x
import board
import busio
import digitalio
from digitalio import DigitalInOut
import serial
import io


def init_radio(sck, mosi, miso, cs, reset):
    """Initialize the radio"""
    logging.info("Initializing transmitter")
    spi = busio.SPI(sck, MOSI=mosi, MISO=miso)
    cs = DigitalInOut(cs)
    reset = DigitalInOut(reset)
    rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)
    rfm9x.tx_power = 23
    return rfm9x


def init_altimeter():
    """Initialize the sensor for pressure, temperature, and altitude"""
    logging.info("Initializing altimeter")
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    cs = digitalio.DigitalInOut(board.D5)
    bmp = adafruit_bmp3xx.BMP3XX_SPI(spi, cs)
    return bmp


def init_magnetometer_accelerometer():
    """Initialize the sensor for magnetic and acceleration"""
    i2c = busio.I2C(board.SCL, board.SDA)
    mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
    accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
    return mag, accel

def init_gps():
    """Initialize the serial port to receive GPS data"""
    ser = serial.Serial("/dev/ttyS0", 9600, timeout=5.0)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    return sio

def gps_reception_loop(gps_value: AtomicValue):
    """Loop forever reading GPS data and passing it to an atomic value"""
    sio = init_gps()
    while True:
        try:
            line = sio.readline()
            if line[0:6] == "$GPRMC":
                gps = pynmea2.parse(line)
                gps_value.update((
                    gps.latitude if gps else 0.0,
                    gps.longitude if gps else 0.0,
                    gps.gps_qual if gps else 0.0,
                    gps.num_sats if gps else 0.0
                ))
        except Exception as ex:
            logging.error("Telemetry reading failure: %s", str(ex))
            logging.exception(ex)
        time.sleep(0)
