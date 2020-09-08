import math
import random
import time

def next_y(x):
    apogee_point = 0.25
    if x <= apogee_point:
        y = -16 * math.pow(x - apogee_point, 2) + 1
    else:
        y = -1.776 * math.pow(x - apogee_point, 2) + 1
    jitter = ((random.random() - 0.5) * 0.00001)
    return y + jitter

def generate_data():
    ground_temp = 15
    apogee_temp = 10
    apogee_height = 300
    step = 0.001
    x = 0
    with open(f"./data/test_data_{int(time.time())}.csv", "w") as data_file:
        while x <= 1:
            y = next_y(x)
            altitude = apogee_height * y
            pressure = 1013.25 * math.exp(-0.00012 * altitude)
            temperature = ground_temp + ((apogee_temp - ground_temp) * y)
            data_file.write(",".join([str(pressure), str(temperature), str(altitude)]) + "\n")
            x += step

if __name__ == "__main__":
    generate_data()
