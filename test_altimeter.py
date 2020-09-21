import os

import adafruit_bmp3xx
import board
import busio
import digitalio

SPI = busio.SPI(board.SCK, board.MOSI, board.MISO)
CS = digitalio.DigitalInOut(board.D5)
bmp = adafruit_bmp3xx.BMP3XX_SPI(SPI, CS)
bmp.sea_level_pressure = float(os.getenv("PRESSURE_AT_SEA_LEVEL", 1013.25))

print(f"Alt: {bmp.altitude}")
print(f"Temp: {bmp.temperature}")
print(f"Pres: {bmp.pressure}")
