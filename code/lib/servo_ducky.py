
import os
import asyncio
import board
import supervisor
import time

from adafruit_pca9685 import PCA9685
from adafruit_motor import servo





class servoducky():


    SERVO_DEFAULTS = { }



    SERVO_DEFAULTS["actuation_range"] = os.getenv("default_actuation_range")
    SERVO_DEFAULTS["min_pulse"] = os.getenv("default_min_pulse")
    SERVO_DEFAULTS["max_pulse"] = os.getenv("default_max_pulse")
    SERVO_DEFAULTS["locked"]    = os.getenv("default_locked")

    if SERVO_DEFAULTS["locked"].lower() == "true":
        SERVO_DEFAULTS["locked"] = True
    else:
        SERVO_DEFAULTS["locked"] = False



    CLASS_DEFAULTS = { }
    CLASS_DEFAULTS["script_dir"] = "/scripts"
    CLASS_DEFAULTS["servo_configs"] = { }
    CLASS_DEFAULTS["number_of_servos"] = 16
    CLASS_DEFAULTS["neopixel_pin"] = board.GP16






    def __init__(self,**kwargs):



        try:
            import neopixel
            self.NEOPIXEL_LIB = True
        except Exception as e:
            self.NEOPIXEL_LIB = False



        self.class_args = kwargs

        for param in self.CLASS_DEFAULTS:
            if param not in self.class_args:
                self.class_args[param] = self.CLASS_DEFAULTS[param]


        script_dir = self.class_args["script_dir"]

        try:
            os.stat(script_dir)
        except Exception as e:
            print("Unable to find script dir")
            print("Exception is:")
            print(e)
            raise Exception()

        if not script_dir.endswith("/"):
            script_dir += "/"

        self.class_args["script_dir"] = script_dir

        self._list_scripts()
        self.__init_servos__()

        if self.NEOPIXEL_LIB:
            self.status_led =  neopixel.NeoPixel(self.class_args["neopixel_pin"], 1, brightness=0.5, auto_write=True)
            self.set_status_led("green")

    def set_status_led(self,color):

        colors = { }

        colors["red"] = (255, 0, 0)
        colors["yellow"] = (255, 150, 0)
        colors["green"] = (0, 255, 0)
        colors["cyan"] = (0, 255, 255)
        colors["blue"] = (0, 0, 255)
        colors["purple"] = (180, 0, 255)


        self.status_led.fill(colors[color])
        self.status_led.show()




    def __init_servos__(self):


        self.servos = { }

        for i in range(self.class_args["number_of_servos"]):
            self.servos[str(i)] = { }

        for servo_id in self.servos:
            self.servos[servo_id]["channel"] = int(servo_id)

            for entry in self.SERVO_DEFAULTS:
                if entry not in self.servos[servo_id]:
                    self.servos[servo_id][entry] = self.SERVO_DEFAULTS[entry]

        for servo_id in self.servos:

            sc = self.servos[servo_id]
            pca = self.class_args["pca"]

            self.servos[servo_id]["servo"] = servo.Servo(pca.channels[sc["channel"]], min_pulse=sc["min_pulse"], max_pulse=sc["max_pulse"], actuation_range=sc["actuation_range"])


    def _list_servos(self):

        servo_list = [ ]
        servo_info = [ ]

        for servo in self.servos:
            servo_list.append(int(servo))

        servo_list.sort()

        for servo in servo_list:
            servo_data = self.servos[str(servo)]

            servo_id = servo
            servo_range = servo_data["actuation_range"]
            servo_angle = self.servos[str(servo_id)]["servo"].angle

            if not servo_angle:
                servo_angle = "Err_none"

            elif servo_angle < 0:
                servo_angle = 0
            elif servo_angle > servo_range:
                servo_angle = "Err_read-error"

            servo_info.append([servo_id,servo_range,servo_angle])


        #servo_info.append("DONE")

        return servo_info




    def read_script(self,script):



        config = script

        sections = { }

        section = "na"

        for line in config.split("\n"):
            if line.strip() == "":
                continue

            line = line.split("#")[0]
            line = line.strip()
            if line.startswith("["):
                section = line.replace("[","").replace("]","")
                if section not in sections:
                    sections[section] = [ ]
            else:
                sections[section].append(line)

        return sections

    def _list_scripts(self):

        script_dir = self.class_args["script_dir"]

        all_files = os.listdir(script_dir)
        scode_files = { }
        for file in all_files:
            if not file.startswith("."):
                if file.endswith(".scode"):
                    full_path = script_dir + file
                    script_name = file.split(".scode")[0]
                    scode_files[script_name] = full_path

        self.scripts = scode_files





    async def run_script(self,script_name):

        if script_name not in self.scripts:
            print("script not found")
            return

        script_contents = open(self.scripts[script_name],"r").read()
        script = self.read_script(script_contents)

        function_name = "main"
        await self._execute_function(script,function_name)

    async def run_tmp_script(self,tmp_script):

        script_name = tmp_script
        function_name = "main"

        script = self.read_script(script_name)


        await self._execute_function(script,function_name)


    async def _execute_function(self,script,function_name,params=[]):

        function = script[function_name]
        for line in function:
            await self.execute_command(line,script,params)

    async def execute_command(self,line,script="",params=[]):

            print("Executing command: " + line)
            line_split = line.split()



            if "_" in line:

                line_parts = [ ]

                for entry in line_split:
                    if entry.startswith("_"):

                        var_id = int(entry.replace("_",""))
                        var_value = params[var_id]

                        line_parts.append(var_value)

                    else:
                        line_parts.append(entry)

                line = " ".join(line_parts)
                #line = line.replace(var_string,var_value)


            if line.startswith("S"):


                line = line[1:]
                line_split = line.split()



                line = line[1:]


                servo_id = line_split[0]




                if servo_id not in self.servos:
                    print("Invalid servo: " + servo_id)
                    return


                try:
                    servo_angle = int(line_split[1])
                except:
                    print(line_split[1] + " is not an interger")
                    return





                actuation_range = self.servos[servo_id]["servo"].actuation_range
                if servo_angle > actuation_range:
                    print("WARNING: ")
                    print('LINE: "' + line + '" is invalid')
                    print("movement is defined at: " + str(servo_angle) + "° but the max range is: " + str(actuation_range) +"°")
                    print("reducing angle to: " + str(actuation_range))
                    servo_angle = actuation_range


                if len(line_split) == 2:
                    print("setting servo: " + servo_id + " to angle " + str(servo_angle))
                    self.servos[servo_id]["servo"].angle = servo_angle
                else:


                    servo_time = int(line_split[2])

                    if servo_time == 0:
                        servo_time = 1




                    current_pos = int(self.servos[servo_id]["servo"].angle)



                    if current_pos > 400:
                        current_pos = 1


                    pos_diff = int(abs(current_pos - servo_angle))




                    delay_time = (servo_time / pos_diff) / 100

                    print("setting servo: " + servo_id + " from angle " + str(current_pos) + " to angle " + str(servo_angle) + " in: " + str(servo_time) + " ms")

                    step_val = 1
                    if servo_angle < current_pos:
                        step_val = step_val * -1


                    invalid_step = True

                    start_step_time_ms = supervisor.ticks_ms()
                    start_step_time_s = time.monotonic()


                    for step in range(current_pos,servo_angle,step_val):
                        invalid_step = False
                        print("Stepping servo: " + servo_id + " to " + str(step) )
                        self.servos[servo_id]["servo"].angle = step
                        await asyncio.sleep(delay_time)

                    if invalid_step:
                        print("else break")
                        self.servos[servo_id]["servo"].angle = servo_angle


                    stop_step_time_ms = supervisor.ticks_ms()
                    stop_step_time_s = time.monotonic()

                    delta_step_time_ms = stop_step_time_ms - start_step_time_ms
                    delta_step_time_s = stop_step_time_s - start_step_time_s
                    print(delta_step_time_ms)
                    print(delta_step_time_s)


            elif line.upper().startswith("DELAY"):


                if len(line_split) < 2:
                    print("No delay time specified in line: " + line)
                    delay_time = 100
                else:
                    delay_time = line_split[1]

                delay_time = float(delay_time)

                delay_time = delay_time / 100

                print("sleeping for: " + str(delay_time))

                await asyncio.sleep(delay_time)

            elif line.startswith("R"):
                params = line.split()
                params.pop(0)
                routine = params[0]
                params.pop(0)

                print("executing function: " + routine + " with params: " + str(params))
                await self._execute_function(script,routine,params)

            elif line.startswith("G"):

                print(line)
                params = line.split()
                params.pop(0)
                if params[0].startswith("S"):
                    pass








if __name__ == "__main__":

    import busio
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





    async def main():


        #import circuitpython_base64 as base64



        #script_base64 = "W21haW5dClMwIDAKREVMQVkgMTUwICMgaGVsbG8gdGhlcmUKUzAgMTgwICAzMDAK"


        #script_decoded = base64.decodebytes(script_base64.encode()).decode()
        #asyncio.run(s.run_tmp_script(script_decoded))


        #print(s._list_servos())
        #await s.run_script("ES1")

        script_name = "func_debug"

        asyncio.run(s.run_script(script_name))
        #print(s.scripts)
        #await s.execute_command("DELAY 100 ")
        #await s.execute_command("S0 180 2000")

    asyncio.run(main())



