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




step_times = [ ]

# generate list of step times to measure
s1 = list(range(1,50))
s2 = list(range(50,2501,50))
step_times.extend(s1)
step_times.extend(s2)



# go to initial position
s.execute_command("S0 0")
time.sleep(1)

# for each defined time to measure
async def perform_test(step_time):

    # get pre/post timestamps from 0° to 180°
    a = supervisor.ticks_ms()
    await s.execute_command("S0 180 " + str(step_time))
    b = supervisor.ticks_ms()

    # wait between going back and forth
    await s.execute_command("DELAY 500")

    # get pre/post timestamps from 180° to 0°
    c = supervisor.ticks_ms()
    await s.execute_command("S0 0 " + str(step_time))
    d = supervisor.ticks_ms()

    # calculate the diffirences between timestamps
    x = b - a
    y = d -c

    # calculate the average
    z = ( x + y ) / 2

    # calculate the ratio
    R = z / step_time


    # format choices
    delim = "|" # Delimiter for printout
    ots = "."   # old thousands seperator
    nts = ","   # new thousands seperator

    line = ""
    line += str(step_time) + delim
    line += str(z).replace(ots,nts) + delim
    line += str(R).replace(ots,nts)

    print(line)

def main():

    for step_time in step_times:
        await perform_test(step_time)

asyncio.run(main())

