import adafruit_bmp3xx
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)
mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)

(acceleration_x, acceleration_y, acceleration_z) = accel.acceleration
(magnetic_x, magnetic_y, magnetic_z) = mag.magnetic

print(f"Mag: {magnetic_x} {magnetic_y} {magnetic_z}")

print(f"Accel: {acceleration_x} {acceleration_y} {acceleration_z}")
