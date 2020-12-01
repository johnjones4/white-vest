"""Class to manage system configuration"""
from typing import Dict

import yaml

from whitevest.lib.const import TESTING_MODE

if not TESTING_MODE:
    import board
    from adafruit_blinka.microcontroller.bcm283x.pin import Pin
else:

    class Pin:  # pylint: disable=too-few-public-methods
        """Dummy class for when GPIO modules are not available"""


class Configuration:
    """Class to manage system configuration"""

    def __init__(self, config_file: str, default_configuration):
        """Create a new configuration based on the supplied yml file path or a default config"""
        if config_file:
            try:
                with open(config_file, "r") as config_file_handle:
                    self.config = yaml.full_load(config_file_handle)
            except:  # pylint: disable=bare-except
                pass
            return
        self.config = default_configuration

    def get(self, key: str, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)

    def get_device_configuration(self, device: str, key: str, default=None):
        """Get a device configuration value"""
        if device in self.config.get("devices", {}):
            return self.config["devices"][device].get(key, default)
        return None

    def get_pin_assignments(self, device: str) -> Dict[str, Pin]:
        """Get a set of pin assignments for a device"""
        if device in self.config.get("devices", {}):
            config = self.config["devices"][device]
            assignments = {}
            for name in config:
                assignments[name] = getattr(board, config[name])
            return assignments
        return None

    default_air_configuration = dict(
        runtime_limit=6000,
        output_directory="./data",
        devices=dict(
            rfm9x=dict(
                sck="SCK_1",
                mosi="MOSI_1",
                miso="MISO_1",
                cs="D24",
                reset="CE0",
            ),
            bmp3xx=dict(
                sck="SCK",
                mosi="MOSI",
                miso="MISO",
                cs="D5",
            ),
            lsm303=dict(
                scl="SCL",
                sda="SDA",
            ),
            gps=dict(
                serial_device="/dev/ttyS0",
            ),
        ),
    )

    default_ground_configuration = dict(
        output_directory="./data",
        streaming_server_port=5678,
        http_server_port=8000,
        devices=dict(
            rfm9x=dict(
                sck="SCK",
                mosi="MOSI",
                miso="MISO",
                cs="CE1",
                reset="D25",
            )
        ),
    )
