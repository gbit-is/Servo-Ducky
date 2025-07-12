import board
import busio
import time
import os
import json

import usb_cdc

from servo_ducky import servoducky
import asyncio
from adafruit_pca9685 import PCA9685

import circuitpython_base64 as base64

# https://github.com/jimbobbennett/CircuitPython_Base64






import supervisor
supervisor.runtime.autoreload = False


WHOIS_ID = "servo_ducky_v0"


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



uart = usb_cdc.data

s = servoducky(pca=pca,uart=uart)


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
        serial_command = serial_command.strip()

        #serial_command = serial_command.upper()



        if serial_command.upper().startswith("R"):
            script_name = serial_command.split()[1]
            print("From Serial|Executing script: " + script_name)

            print(script_name)

            asyncio.run(s.run_script(script_name))

        elif "WHOIS" in serial_command.upper():
            uart.write(WHOIS_ID)

        elif "LIST_SERVOS" in serial_command.upper():
            print("list servos to uart")
            servo_info = s._list_servos()
            servo_info.append("DONE")
            uart.write(json.dumps(servo_info))

        elif serial_command.upper().startswith("LOAD"):


            script_base64 = serial_command.split("|")[1]
            script_decoded = base64.decodebytes(script_base64.encode()).decode()

            print("LOADING SCRIPT OVER UART")
            asyncio.run(s.run_tmp_script(script_decoded))


        elif serial_command.upper().startswith("LIST"):
            print("Requesting list of scripts")

            scripts = [ ]
            for script in s.scripts:
                scripts.append(script)

            script.append("DONE")

            uart.write(json.dumps(scripts))

        elif "SDCC_INIT" in serial_command.upper():

            ducky_info = [ ]

            servo_info = s._list_servos()

            ducky_info.append(servo_info)

            scripts = [ ]
            for script in s.scripts:
                scripts.append(script)

            ducky_info.append(scripts)
            ducky_info.append("DONE")
            print(ducky_info)
            uart.write(json.dumps(ducky_info))

        elif "DEBUG" in serial_command.upper():
            if "ENABLE" in serial_command.upper():
                s.class_args["debug_uart"] = True
            elif "DISABLE" in serial_command.upper():
                s.class_args["debug_uart"] = False



        else:

            serial_command = serial_command.upper()

            serial_command = serial_command.strip()

            print("From Serial|Executing command: " + serial_command)
            asyncio.run(s.execute_command(serial_command))













