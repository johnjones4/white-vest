import time

import adafruit_rfm9x
import board
import busio
from digitalio import DigitalInOut

spi = busio.SPI(board.SCK_1, MOSI=board.MOSI_1, MISO=board.MISO_1)
cs = DigitalInOut(board.D24)
reset = DigitalInOut(board.CE0)
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0, baudrate=1000000)
rfm9x.tx_power = 23
while True:
    for char_code in range(65, 91):
        char = chr(char_code).encode("utf-8")
        print(f"Sending: {char}")
        rfm9x.send(char)
        print("Sent")
        time.sleep(1)
