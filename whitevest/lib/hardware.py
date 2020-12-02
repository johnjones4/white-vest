"""Utils for setting up hardware access"""
import io
import logging

import adafruit_bmp3xx
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
import adafruit_rfm9x
import busio
import digitalio
import serial
import board
from digitalio import DigitalInOut

from whitevest.lib.configuration import Configuration


def init_radio(configuration: Configuration):
    """Initialize the radio"""
    logging.info("Initializing transmitter")
    assignments = configuration.get_pin_assignments("rfm9x")
    if not assignments:
        return None
    spi = busio.SPI(
        assignments.get("sck"),
        MOSI=assignments.get("mosi"),
        MISO=assignments.get("miso"),
    )
    cs = DigitalInOut(assignments.get("cs"))  # pylint: disable=invalid-name
    reset = DigitalInOut(assignments.get("reset"))
    rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)
    rfm9x.tx_power = 23
    return rfm9x


def init_altimeter(configuration: Configuration):
    """Initialize the sensor for pressure, temperature, and altitude"""
    logging.info("Initializing altimeter")
    assignments = configuration.get_pin_assignments("bmp3xx")
    if not assignments:
        return None
    spi = busio.SPI(
        assignments.get("sck"), assignments.get("mosi"), assignments.get("miso")
    )
    cs = digitalio.DigitalInOut(assignments.get("cs"))  # pylint: disable=invalid-name
    bmp = adafruit_bmp3xx.BMP3XX_SPI(spi, cs)
    return bmp


def init_magnetometer_accelerometer(configuration: Configuration):
    """Initialize the sensor for magnetic and acceleration"""
    assignments = configuration.get_pin_assignments("lsm303")
    if not assignments:
        return None, None
    i2c = busio.I2C(assignments.get("scl"), assignments.get("sda"))
    mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
    accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
    return mag, accel


def init_gps(configuration: Configuration):
    """Initialize the serial port to receive GPS data"""
    gps_serial_port = configuration.get_device_configuration("gps", "serial_device")
    if not gps_serial_port:
        return None
    ser = serial.Serial(gps_serial_port, 9600, timeout=5.0)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
    return sio
