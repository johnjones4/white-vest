"""Tests reading data from sensors"""
from whitevest.lib.hardware import (
    init_altimeter,
    init_magnetometer_accelerometer
)
import logging

if __name__ == "__main__":
    bmp = init_altimeter()
    (pressure, temperature) = bmp.read()
    logging.info("Pressure: %f", pressure)
    logging.info("Temperature: %f", temperature)

    mag, accel = init_magnetometer_accelerometer()
    logging.info("Mag: %f %f %f", *mag)
    logging.info("Accel: %f %f %f", *accel)
