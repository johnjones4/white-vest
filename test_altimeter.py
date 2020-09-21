import board
import busio
import adafruit_bmp3xx
import digitalio
import os

SPI = busio.SPI(board.SCK, board.MOSI, board.MISO)
CS = digitalio.DigitalInOut(board.D5)
bmp = adafruit_bmp3xx.BMP3XX_SPI(SPI, CS)
bmp.sea_level_pressure = float(os.getenv("PRESSURE_AT_SEA_LEVEL", 1013.25))

print(f"Alt: {bmp.altitude}")
print(f"Temp: {bmp.temperature}")
print(f"Pres: {bmp.pressure}")
