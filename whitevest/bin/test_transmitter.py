import time
import logging

import board

from whitevest.lib.hardware import init_radio

rfm9x = init_radio(
    board.SCK_1, board.MOSI_1, board.MISO_1, board.D24, board.CE0
)
while True:
    for char_code in range(65, 91):
        char = chr(char_code).encode("utf-8")
        logging.info("Sending: %s", char)
        rfm9x.send(char)
        logging.info("Sent")
        time.sleep(1)
