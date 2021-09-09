"""Take a reading from each sensor to test its functionality"""
import logging
import os
import time

from whitevest.lib.atomic_buffer import AtomicBuffer
from whitevest.lib.atomic_value import AtomicValue
from whitevest.lib.configuration import Configuration
from whitevest.lib.const import TELEMETRY_TUPLE_LENGTH
from whitevest.lib.hardware import (
    init_altimeter,
    init_gps,
    init_magnetometer_accelerometer,
    init_radio,
)
from whitevest.lib.utils import (
    handle_exception,
    take_gps_reading,
    transmit_latest_readings,
)

TEST_TIME_LENGTH = 30


def main():
    """Take a reading from each sensor to test its functionality"""
    # Load up the system configuration
    configuration = Configuration(
        os.getenv("AIR_CONFIG_FILE", None), Configuration.default_air_configuration
    )
    # configuration = Configuration(
    #     os.getenv("GROUND_CONFIG_FILE", None), Configuration.default_ground_configuration
    # )

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
            camera_is_running = AtomicValue(0.0)
            current_reading = AtomicBuffer(2)
            current_reading.put([0.0 for _ in range(TELEMETRY_TUPLE_LENGTH)])
            current_reading.put([0.0 for _ in range(TELEMETRY_TUPLE_LENGTH)])
            start_time = time.time()
            transmissions = 0
            while time.time() - start_time < TEST_TIME_LENGTH:
                transmit_latest_readings(
                    camera_is_running, rfm9x, 0, 0, 0, current_reading
                )
                transmissions += 1
            total_time = time.time() - start_time
            logging.info(
                "Transmitted %d messages at an average rate of %f/sec",
                transmissions,
                float(transmissions) / total_time,
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
            pressure = 0.0
            temperature = 0.0
            readings = 0
            while time.time() - start_time < TEST_TIME_LENGTH:
                (
                    pressure,
                    temperature,
                ) = bmp._read()  # pylint: disable=protected-access
                readings += 1
            total_time = time.time() - start_time
            logging.info(
                "Last bmp3xx reading: %f %f out of %d readings at an average rate of %f/sec",
                pressure,
                temperature,
                readings,
                float(readings) / total_time,
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
            acceleration = (0.0, 0.0, 0.0)
            magnetic = (0.0, 0.0, 0.0)
            readings = 0
            while time.time() - start_time < TEST_TIME_LENGTH:
                acceleration = accel.acceleration
                magnetic = mag.magnetic
                readings += 1
            total_time = time.time() - start_time
            logging.info(
                "Last lsm303dlh acceleration and magnetic reading: %f %f %f %f %f %f out of %d readings at an average rate of %f/sec",  # pylint: disable= line-too-long
                *acceleration,
                *magnetic,
                readings,
                float(readings) / total_time,
            )
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
            readings = 0
            while readings < 10 or time.time() - start_time < TEST_TIME_LENGTH:
                try:
                    if take_gps_reading(gps, gps_value):
                        readings += 1
                except Exception as ex:  # pylint: disable=broad-except:
                    handle_exception("Reading failure", ex)
            total_time = time.time() - start_time
            logging.info(
                "Last GPS reading: %f, %f, %f, %f out of %d readings at an average rate of %f/sec",
                *gps_value.get_value(),
                readings,
                float(readings) / total_time,
            )
        else:
            logging.info("No GPS hardware configured")
    except Exception as ex:  # pylint: disable=broad-except
        handle_exception("GPS failure", ex)


if __name__ == "__main__":
    main()
