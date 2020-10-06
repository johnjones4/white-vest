import time
import logging

import board

from whitevest.lib.hardware import init_radio

rfm9x = init_radio(board.SCK, board.MOSI, board.MISO, board.CE1, board.D25)
logging.info("Ready to receive")
while True:
    packet = rfm9x.receive()
    if packet:
        logging.info("Received: %s", str(packet, "utf-8"))
    time.sleep(0)
