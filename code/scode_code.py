import board
import busio
import time
import os

import usb_cdc

from servo_ducky import servoducky
import asyncio
from adafruit_pca9685 import PCA9685


import supervisor
supervisor.runtime.autoreload = False



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

uart = usb_cdc.data


serial_data = b""

break_characters = [ "@", "\r" ]


while True:



    #asyncio.run(s.execute_command("S0 0"))
    #asyncio.run(s.execute_command("DELAY 100"))
    #asyncio.run(s.execute_command("S0 180"))

    data = uart.read(1)

    serial_data += data

    #print("....." + str(serial_data))
    #print(type(serial_data))



    if any(breaking_character in serial_data for breaking_character in break_characters):
        serial_command = serial_data

        serial_command = serial_command.decode()

        serial_data = b""

        #print(str(serial_command) + "___")
        serial_command = serial_command.replace("@","")

        #serial_command = serial_command.upper()

        if serial_command.upper().startswith("R"):
            script_name = serial_command.split()[1]
            print("From Serial|Executing script: " + script_name)

            asyncio.run(s.run_script(script_name))
        else:

            serial_command = serial_command.upper()

            print("From Serial|Executing command: " + serial_command)
            asyncio.run(s.execute_command(serial_command))













