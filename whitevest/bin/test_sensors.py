"""Take a reading from each sensor to test its functionality"""
import logging
import os
import time

from whitevest.lib.air import transmit_latest_readings
from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.configuration import Configuration
from whitevest.lib.const import TELEMETRY_TUPLE_LENGTH
from whitevest.lib.hardware import (
    init_altimeter,
    init_gps,
    init_magnetometer_accelerometer,
    init_radio,
)
from whitevest.lib.utils import handle_exception, take_gps_reading


def main():
    """Take a reading from each sensor to test its functionality"""
    # Load up the system configuration
    configuration = Configuration(
        os.getenv("AIR_CONFIG_FILE", None), Configuration.default_air_configuration
    )

    test_rfm9x(configuration)
    test_bmp3xx(configuration)
    test_lsm303dlh(configuration)
    test_gps(configuration)


def test_rfm9x(configuration: Configuration):
    """Transmit on the rfm9x to test its functionality"""
    try:
        logging.info("Testing rfm9x ...")
        rfm9x = init_radio(configuration)
        if rfm9x:
            current_reading = AtomicValue([0.0 for _ in range(TELEMETRY_TUPLE_LENGTH)])
            start_time = time.time()
            transmit_latest_readings(rfm9x, 0, 0, 0, current_reading)
            logging.info(
                "Transmission complete in %f seconds", time.time() - start_time
            )
        else:
            logging.info("No rfm9x hardware configured")
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("rfm9x failure", ex)


def test_bmp3xx(configuration: Configuration):
    """Take a reading from the bmp3xx to test its functionality"""
    try:
        logging.info("Testing bmp3xx ...")
        bmp = init_altimeter(configuration)
        if bmp:
            start_time = time.time()
            (pressure, temperature) = bmp._read()  # pylint: disable=protected-access
            logging.info(
                "bmp3xx reading: %f %f in %f seconds",
                pressure,
                temperature,
                time.time() - start_time,
            )
        else:
            logging.info("No bmp3xx hardware configured")
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("bmp3xx failure", ex)


def test_lsm303dlh(configuration: Configuration):
    """Take a reading from the lsm303dlh to test its functionality"""
    try:
        logging.info("Testing lsm303dlh ...")
        (mag, accel) = init_magnetometer_accelerometer(configuration)
        if mag and accel:
            start_time = time.time()
            logging.info(
                "lsm303dlh acceleration reading: %f %f %f", *accel.acceleration
            )
            logging.info("lsm303dlh magnetic reading: %f %f %f", *mag.magnetic)
            logging.info("Reading complete in %f seconds", time.time() - start_time)
        else:
            logging.info("No lsm303dlh hardware configured")
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("lsm303dlh failure", ex)


def test_gps(configuration: Configuration):
    """Take a reading from the gps to test its functionality"""
    try:
        logging.info("Testing gps ...")
        gps = init_gps(configuration)
        if gps:
            gps_value = AtomicValue()
            start_time = time.time()
            i = 0
            while not take_gps_reading(gps, gps_value) and i < 1000:
                i += 1
            logging.info(
                "GPS reading: %f, %f, %f, %f complete in %f seconds",
                *gps_value.get_value(),
                time.time() - start_time
            )
        else:
            logging.info("No GPS hardware configured")
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("GPS failure", ex)


if __name__ == "__main__":
    main()
