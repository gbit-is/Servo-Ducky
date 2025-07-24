import asyncio
import usb_cdc
import board
import busio
import time
import os
import json
import digitalio
from servo_ducky import servoducky
from adafruit_pca9685 import PCA9685
import supervisor

import circuitpython_base64 as base64
uart = usb_cdc.data

WHOIS_ID = "servo_ducky_v0"
DO_AUTO_RELOAD = False



supervisor.runtime.autoreload = DO_AUTO_RELOAD

PCA_PINS = { }
PCA_PINS["SCL_PIN"] = { "default" : 27 }
PCA_PINS["SDA_PIN"] = { "default" : 26 }
PCA_PINS["OE_PIN"]  = { "default" : 28 }

for PCA_PIN in PCA_PINS:
    if os.getenv(PCA_PIN):
        pin_number = os.getenv(PCA_PIN)
    else:
        pin_number = PCA_PINS[PCA_PIN]["default"]

    pin_name = "GP" + str(pin_number)
    PCA_PINS[PCA_PIN] = getattr(board,pin_name)

# Store all running tasks
running_tasks = set()

def print_to_serial(msg,header=True):

    if header:
        uart.write("FP: " + str(msg) + "\n")
    else:
        uart.write(str(msg) + "\n")
    print(str(msg))

# Example action function
async def do_action(name: str, duration: float):
    #print(f"Starting action: {name}")
    try:
        await asyncio.sleep(duration)  # Simulate work
        #print(f"Finished action: {name}")
    except asyncio.CancelledError:
        #print(f"Cancelled action: {name}")
        raise

# Wrapper to manage lifecycle
async def track_task(coro):

    task = asyncio.create_task(coro)
    running_tasks.add(task)

    try:
        await task
    except asyncio.CancelledError:
        pass
    running_tasks.discard(task)

# Command dispatcher
async def handle_command(command: str):



    command = command.strip()

    if command.upper().startswith("R"):
        try:
            script_name = command.split()[1]
            await s.run_script(script_name)
            asyncio.create_task(track_task(s.run_script(script_name)))
        except Exception as e:
            print_to_serial("Error running R command: " + command )
            print_to_serial(str(e))

    elif command.upper().startswith("S"):

        try:
            asyncio.create_task(track_task(s.execute_command(command.upper())))
        except Exception as e:
            print_to_serial("Error running S command: " + command)
            print_to_serial(e)


    elif "SDCC_INIT" in command.upper():
        ducky_info = [
            s._list_servos(),
            list(s.scripts),
            {"debug": s.class_args["debug_uart"]},
            "DONE"
        ]
        print_to_serial(json.dumps(ducky_info),False)

    elif command.upper().startswith("LOAD"):



        script_base64 = command.split("|")[1]
        try:
            script_base64 = command.split("|")[1]
            script_decoded = base64.decodebytes(script_base64.encode()).decode()
            asyncio.create_task(track_task(s.run_tmp_script(script_decoded)))
            s.debug("C: Done running loaded script\n")
        except Exception as e:
            print_to_serial("Unable to run load command")
            print(e)
            print_to_serial(e)



    elif "DEBUG" in command.upper():

        if "ENABLE" in command.upper():
            s.class_args["debug_uart"] = True
        elif "DISABLE" in command.upper():
            s.class_args["debug_uart"] = False
        elif "CHECK" in command.upper():
            print_to_serial(str(s.class_args["debug_uart"]))

    elif "WHOIS" in command.upper():
        print_to_serial(WHOIS_ID)

    elif command == "cancel_all":
        print_to_serial("Cancelling all actions...")
        s.debug("Cancelling all actions...\n")
        for task in list(running_tasks):
            task.cancel()
    elif command == "_reload":


        print_to_serial("Reloading code.py")
        print_to_serial("this might break any terminal connections")
        supervisor.reload()


    else:
        print_to_serial("Invalid command: " + command)



# Async UART listener
async def uart_listener():
    buffer = ""
    print("UART listener started.")
    while True:
        if uart.in_waiting > 0:
            c = uart.read(1).decode("utf-8")
            if c == "\n":

                asyncio.create_task(track_task(handle_command(buffer)))
                #await handle_command(buffer)
                buffer = ""
            else:
                buffer += c

        await asyncio.sleep(0.01)

# Main entry point
async def main():
    asyncio.create_task(uart_listener())
    while True:
        await asyncio.sleep(1)


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

        #POWER_PINS[POWER_PIN]["DIO"].value = not POWER_PINS[POWER_PIN]["VALUE"]
        POWER_PINS[POWER_PIN]["DIO"].value = POWER_PINS[POWER_PIN]["VALUE"]
time.sleep(1)

PCA_FREQ = 60
PCA_DUTY_CYCLE = 0x7FFF
NUMBER_OF_SERVOS = 4

i2c = busio.I2C(PCA_PINS["SCL_PIN"],PCA_PINS["SDA_PIN"])    # Pi Pico RP2040
pca = PCA9685(i2c)
pca.frequency = PCA_FREQ
pca.channels[0].duty_cycle = PCA_DUTY_CYCLE
s = servoducky(pca=pca,uart=uart)

if "init" in s.scripts:
    print("Running init script")
    s.run_script("init")

asyncio.run(main())
