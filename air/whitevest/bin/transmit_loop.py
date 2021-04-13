import logging
import os
import time

from whitevest.lib.configuration import Configuration
from whitevest.lib.hardware import (
    init_radio,
)

def main():
    configuration = Configuration(
        os.getenv("AIR_CONFIG_FILE", None), Configuration.default_air_configuration
    )
    rfm9x = init_radio(configuration)
    if rfm9x:
        while True:
            logging.info("Sending")
            rfm9x.send(b"TEST")
            time.sleep(1)

if __name__ == "__main__":
    main()
