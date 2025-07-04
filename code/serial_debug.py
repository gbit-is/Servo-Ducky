import board
import busio
import time
import os
import neopixel
import usb_cdc
import random


colors = { }

colors["red"] = (255, 0, 0)
colors["yellow"] = (255, 150, 0)
colors["green"] = (0, 255, 0)
colors["cyan"] = (0, 255, 255)
colors["blue"] = (0, 0, 255)
colors["purple"] = (180, 0, 255)

color_list = [ ]
for color in colors:
    color_list.append(colors[color])

np_pin = board.GP16

uart = usb_cdc.data

LED = neopixel.NeoPixel(np_pin, 1, brightness=0.5, auto_write=True)

serial_data = ""

IS_BLUE = False

while True:


    if IS_BLUE:
        c = colors["red"]
        IS_BLUE = False
    else:
        c = colors["blue"]
        IS_BLUE = True

    #c = random.choice(color_list)

    LED.fill(c)
    LED.show()

    data = uart.read(1)



    if data is not None:
        print(data)
    else:
        print("foo")

    time.sleep(1)






# Write your code here :-)
