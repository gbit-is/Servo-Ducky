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



# Store all running tasks
running_tasks = set()

def print_to_serial(msg):

    uart.write(msg + "\n")

# Example action function
async def do_action(name: str, duration: float):
    print(f"Starting action: {name}")
    try:
        await asyncio.sleep(duration)  # Simulate work
        print(f"Finished action: {name}")
    except asyncio.CancelledError:
        print(f"Cancelled action: {name}")
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
        script_name = command.split()[1]
        print("From Serial | Executing script:", script_name)
        await s.run_script(script_name)
        asyncio.create_task(track_task(s.run_script(script_name)))

    elif command.upper().startswith("S"):

        print(running_tasks)

        asyncio.create_task(track_task(s.execute_command(command)))

        #await s.execute_command(serial_command)

    elif "SDCC_INIT" in command.upper():
        ducky_info = [
            s._list_servos(),
            list(s.scripts),
            {"debug": s.class_args["debug_uart"]},
            "DONE"
        ]
        print(ducky_info)
        print_to_serial(json.dumps(ducky_info))

    elif command.upper().startswith("LOAD"):
        script_base64 = command.split("|")[1]
        script_decoded = base64.decodebytes(script_base64.encode()).decode()
        print("Loading script over UART")

        asyncio.create_task(track_task(s.run_tmp_script(script_decoded)))
        s.debug("C: Done running loaded script\n")
        print("Done running loaded script")
        #await s.run_tmp_script(script_decoded)



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
        print("Cancelling all actions...")
        s.debug("Cancelling all actions...\n")
        for task in list(running_tasks):
            task.cancel()
    elif command == "reload":
        supervisor.reload()
    else:
        print("Invalid command: " + command)
        s.debug("Invalid command: " + command + "\n")



# Async UART listener
async def uart_listener():
    buffer = ""
    print("UART listener started.")
    while True:
        if uart.in_waiting > 0:
            c = uart.read(1).decode("utf-8")
            if c == "\n":
                await handle_command(buffer)
                buffer = ""
            else:
                buffer += c
        await asyncio.sleep(0.01)

# Main entry point
async def main():
    asyncio.create_task(uart_listener())
    while True:
        await asyncio.sleep(1)










WHOIS_ID = "servo_ducky_v0"


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

        #POWER_PINS[POWER_PIN]["DIO"].value = not POWER_PINS[POWER_PIN]["VALUE"]
        POWER_PINS[POWER_PIN]["DIO"].value = POWER_PINS[POWER_PIN]["VALUE"]
time.sleep(1)

PCA_FREQ = 60
PCA_DUTY_CYCLE = 0x7FFF
NUMBER_OF_SERVOS = 4

i2c = busio.I2C(SCL_PIN,SDA_PIN)    # Pi Pico RP2040
pca = PCA9685(i2c)
pca.frequency = PCA_FREQ
pca.channels[0].duty_cycle = PCA_DUTY_CYCLE
s = servoducky(pca=pca,uart=uart)






asyncio.run(main())
