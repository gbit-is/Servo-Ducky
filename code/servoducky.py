import board
import busio
import time
from scode_lib import scode_reader
import asyncio

from adafruit_pca9685 import PCA9685
from adafruit_motor import servo


NUMBER_OF_SERVOS = 4


SCL_PIN = board.GP1
SDA_PIN = board.GP0
PCA_FREQ = 60
PCA_DUTY_CYCLE = 0x7FFF



# These defaults are based off the SG-92R defaults specified by adafruit
DEFAULTS = { }
DEFAULTS["actuation_range"] = 180
DEFAULTS["min_pulse"] = 500
DEFAULTS["max_pulse"] = 2600
DEFAULTS["locked"]    = False

# Create the I2C bus interface.
i2c = busio.I2C(SCL_PIN,SDA_PIN)    # Pi Pico RP2040
pca = PCA9685(i2c)
pca.frequency = PCA_FREQ
pca.channels[0].duty_cycle = PCA_DUTY_CYCLE



servo_configs = { }

for i in range(NUMBER_OF_SERVOS):
    servo_configs[str(i)] = { }



for servo_id in servo_configs:
    servo_configs[servo_id]["channel"] = int(servo_id)

    for entry in DEFAULTS:
        if entry not in servo_configs[servo_id]:
            servo_configs[servo_id][entry] = DEFAULTS[entry]


SERVOS = { }

for s in servo_configs:
    sc = servo_configs[s]
    SERVOS[s] = servo.Servo(pca.channels[sc["channel"]], min_pulse=sc["min_pulse"], max_pulse=sc["max_pulse"], actuation_range=sc["actuation_range"])


def send_servo_command(servo,angle):

    SERVOS[servo].angle = float(angle)



async def execute_scode(scode):


    for line in scode:

        line_split = line.split(" ")

        if line.startswith("M"):

            motor_number = line_split[0].replace("M","")
            angle = float(line_split[1])


            if len(line_split) == 2:
                send_servo_command(motor_number,angle)
            elif len(line_split) == 3:
                command_time = int(line_split[2])
                current_pos = int(SERVOS[motor_number].angle)

                pos_diff = int(abs(current_pos - angle))
                delay_time = (command_time / pos_diff) / 100
                print(delay_time)

                for step in range(current_pos,angle,10):
                    send_servo_command(motor_number,step)

                    await asyncio.sleep(delay_time)








            else:
                print("Unable to parse line: " + line)

        elif line.startswith("DELAY"):

            if len(line_split) < 2:
                print("No delay time specified in line: " + line)
                delay_time = 100
            else:
                delay_time = line_split[1]

            delay_time = float(delay_time)

            delay_time = delay_time / 100

            await asyncio.sleep(delay_time)



async def main():

    s = scode_reader()
    x = s.read_script("script1")



    x  = asyncio.create_task(execute_scode(x["main"]))

    await asyncio.gather(x)



asyncio.run(main())


