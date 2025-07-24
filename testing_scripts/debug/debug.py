import busio
import digitalio
import os
import asyncio
import board
import supervisor
import time

from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from servo_ducky import servoducky




SCL_PIN = board.GP27
SDA_PIN = board.GP26
OE_PIN = board.GP28

POWER_PINS = { }

POWER_PINS["GND"] = { }
POWER_PINS["GND"]["BOARD"] = board.GP29
POWER_PINS["GND"]["ENABLED"] = True
POWER_PINS["GND"]["VALUE"] = False

POWER_PINS["VCC"] = { }
POWER_PINS["VCC"]["BOARD"] = board.GP15
POWER_PINS["VCC"]["ENABLED"] = True
POWER_PINS["VCC"]["VALUE"] = True

for POWER_PIN in POWER_PINS:
    if POWER_PINS[POWER_PIN]["ENABLED"]:
        POWER_PINS[POWER_PIN]["DIO"] = digitalio.DigitalInOut(POWER_PINS[POWER_PIN]["BOARD"])
        POWER_PINS[POWER_PIN]["DIO"].direction = digitalio.Direction.OUTPUT
        POWER_PINS[POWER_PIN]["DIO"].value = POWER_PINS[POWER_PIN]["VALUE"]



PCA_FREQ = 60
PCA_DUTY_CYCLE = 0x7FFF

i2c = busio.I2C(SCL_PIN,SDA_PIN)    # Pi Pico RP2040
pca = PCA9685(i2c)
pca.frequency = PCA_FREQ
pca.channels[0].duty_cycle = PCA_DUTY_CYCLE

s = servoducky(pca=pca)


#s.class_args["debug_uart"] = True
s.class_args["debug_console"] = True




# go to initial position
#s.execute_command("S0 180")
#time.sleep(1)

# for each defined time to measure
async def run_thing():

    comm = "es2"

    running_tasks = set()

    #task = asyncio.create_task(s.run_script(comm))
    task = asyncio.create_task(s.execute_command("S[0,2] 90"))
    running_tasks.add(task)
    await task

    #await s.run_script(comm)
    #await asyncio.sleep(0.5)

def main():

    await run_thing()

asyncio.run(main())

