import time

import adafruit_rfm9x
import board
import busio
from digitalio import DigitalInOut

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = DigitalInOut(board.CE1)
reset = DigitalInOut(board.D25)
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0, baudrate=1000000)
print("Ready to receive")
while True:
    packet = rfm9x.receive()
    if packet:
        print("Received " + str(packet, "utf-8"))
    time.sleep(0)
