"""Utils for setting up hardware access"""
import io
import logging

import adafruit_bmp3xx
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
import adafruit_rfm9x
import busio
import digitalio
import RPi.GPIO as GPIO
import serial
from digitalio import DigitalInOut

from whitevest.lib.atomic_value import AtomicValue
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
    rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0, baudrate=10000000)
    rfm9x.tx_power = 23
    return rfm9x


def init_altimeter(configuration: Configuration):
    """Initialize the sensor for pressure, temperature, and altitude"""
    logging.info("Initializing altimeter")
    assignments = configuration.get_pin_assignments("bmp3xx")
    if not assignments:
        return None
    i2c = busio.I2C(assignments.get("scl"), assignments.get("sda"))
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)
    bmp._wait_time = 0  # pylint: disable=protected-access
    return bmp


def init_magnetometer_accelerometer(configuration: Configuration):
    """Initialize the sensor for magnetic and acceleration"""
    logging.info("Initializing magnetometer/accelerometer")
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


def init_reset_button(configuration: Configuration, continue_running: AtomicValue):
    """Setup a listener for reset"""

    def handle_reset_button(_):
        logging.info("Reset button pressed!")
        continue_running.update(False)

    GPIO.setmode(GPIO.BCM)  # pylint: disable=no-member
    channel = int(configuration.get_device_configuration("reset", "pin"))
    GPIO.setup(
        channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN
    )  # pylint: disable=no-member
    GPIO.add_event_detect(  # pylint: disable=no-member
        channel,
        GPIO.RISING,
        callback=handle_reset_button,
        bouncetime=500,  # pylint: disable=no-member
    )
