import board
import busio
import time
import os

from servo_ducky import servoducky
import asyncio
from adafruit_pca9685 import PCA9685




SCL_PIN = board.GP1
SDA_PIN = board.GP0
PCA_FREQ = 60
PCA_DUTY_CYCLE = 0x7FFF
NUMBER_OF_SERVOS = 4

# Create the I2C bus interface.
i2c = busio.I2C(SCL_PIN,SDA_PIN)    # Pi Pico RP2040
pca = PCA9685(i2c)
pca.frequency = PCA_FREQ
pca.channels[0].duty_cycle = PCA_DUTY_CYCLE


s = servoducky(pca=pca)

x = s.servos["1"]["servo"]






