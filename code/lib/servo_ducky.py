
import os
import asyncio
import board
import supervisor
import time
import circuitpython_base64 as base64
import random


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
    CLASS_DEFAULTS["debug_uart"] = False
    CLASS_DEFAULTS["debug_console"] = False
    CLASS_DEFAULTS["MAX_WAIT"] = 50


    actions = { }








    def __init__(self,**kwargs):



        try:
            import neopixel
            self.NEOPIXEL_LIB = True
        except Exception as e:
            self.NEOPIXEL_LIB = False

        self.positive_time_adjuster = 0.89
        self.negative_time_adjuster = 0.89


        self.class_args = kwargs



        for param in self.CLASS_DEFAULTS:
            if param not in self.class_args:
                self.class_args[param] = self.CLASS_DEFAULTS[param]


        script_dir = self.class_args["script_dir"]

        try:
            os.stat(script_dir)
        except Exception as e:
            self.debug("Unable to find script dir")
            self.debug("Exception is:")
            self.debug(e)
            raise Exception()

        if not script_dir.endswith("/"):
            script_dir += "/"

        self.class_args["script_dir"] = script_dir

        self._list_scripts()
        self.__init_servos__()

        if self.NEOPIXEL_LIB:
            self.status_led =  neopixel.NeoPixel(self.class_args["neopixel_pin"], 1, brightness=0.5, auto_write=True)
            self.set_status_led("green")

    def debug(self,message):

        if self.class_args["debug_uart"]:
            if "uart" in self.class_args:
                try:
                    self.class_args["uart"].write("DEBUG: " + str(message) + "\n" )
                except Exception as e:
                    print("Unable to print to UART. Error is:\n" + str(e))
        if self.class_args["debug_console"]:
            print(message)

    def write_to_uart(self,message):
        try:
            self.class_args["uart"].write(str(message) + "\n")
        except:
            pass
        print(message)



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




        self.debug("Running script: " + script_name)

        if script_name not in self.scripts:
            self.debug("script not found")
            return

        if script_name in self.actions:
            self.write_to_uart("Script already running")
            #todo, add some zombie checking logic here
        else:
            self.actions[script_name] = set()
            self.actions[script_name].add(0)

        script_contents = open(self.scripts[script_name],"r").read()
        script = self.read_script(script_contents)

        function_name = "main"
        print("------- A")
        await self._execute_function(script,function_name,script_name)
        print("-------- B")

        self.debug("Finished running script: " + script_name)

    async def run_tmp_script(self,tmp_script):

        script_name = tmp_script
        function_name = "main"

        self.debug("Running script: " + script_name)

        script = self.read_script(script_name)


        await self._execute_function(script,function_name,script_name)

        self.debug("Finished running script: " + script_name)


    async def _execute_function(self,script,function_name,script_name,params=[]):



        function = script[function_name]
        for line in function:


            if "WAIT" not in line:

                line_id = max(self.actions[script_name]) + 1
                self.actions[script_name].add(line_id)



            if "DELAY" in line.upper():
                print("DELAY")
                await self.execute_command(line,script_name,script,params)
            elif "WAIT" in line.upper():
                print("WAIT")
                print(self.actions[script_name])
                await self.execute_command(line,script_name,script,params)

            else:
                ### todo need to add logic here to gather tasks and discard ids based on execution finishing
                asyncio.create_task(self.execute_command(line,script_name,script,params))

            self.actions[script_name].discard(line_id)





    async def execute_command(self,line,script_name="no_script",script="",params=[],line_id=""):


            self.debug("Executing command: " + str(line))
            line_split = line.split()
            orig_line = line


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


            if line.startswith("S"):


                servo_ids = None

                line = line[1:]
                line_split = line.split()

                if "[" in line:


                    servo_raw = line_split[0].replace("[","").replace("]","")

                    if "," in servo_raw:
                        servo_ids = servo_raw.split(",")
                    elif "..." in servo_raw:
                        servo_range = servo_raw.strip().split("...")

                        try:
                            r0 = int(servo_range[0])
                            r1 = int(servo_range[1])

                            servo_ids = list(range(r0,r1 + 1 ))

                        except Exception as e:
                            self.debug("Unable to create a servo range with line " + orig_line)
                            self.debug("Error is:\n" + str(e))



                else:
                    servo_ids = [ line_split[0] ]


                if servo_ids is None:
                    self.debug("No servo id found in line: " + orig_line)
                    return

                for servo_id in servo_ids:

                    servo_id = str(servo_id)

                    if servo_id not in self.servos:
                        self.debug("Invalid servo: " + servo_id)
                        return


                    try:
                        servo_angle = int(line_split[1])
                    except:
                        self.debug(line_split[1] + " is not an interger")
                        return





                    actuation_range = self.servos[servo_id]["servo"].actuation_range
                    if servo_angle > actuation_range:
                        self.debug("WARNING: ")
                        self.debug('LINE: "' + line + '" is invalid')
                        self.debug("movement is defined at: " + str(servo_angle) + "° but the max range is: " + str(actuation_range) +"°")
                        self.debug("reducing angle to: " + str(actuation_range))
                        servo_angle = actuation_range


                    if len(line_split) == 2:
                        self.debug("setting servo: " + servo_id + " to angle " + str(servo_angle))
                        self.servos[servo_id]["servo"].angle = servo_angle
                    else:


                        servo_time = int(line_split[2])

                        if servo_time == 0:
                            servo_time = 1


                        step_sleep_time = 10



                        current_pos = int(self.servos[servo_id]["servo"].angle)



                        if current_pos > 400:
                            current_pos = 1


                        pos_diff = max(int(abs(current_pos - servo_angle)),1)
                        pos_diff = servo_angle - current_pos
                        direction = 1 if pos_diff >= 0 else -1
                        abs_pos_diff = abs(pos_diff)


                        steps_needed = max(1, int(servo_time // step_sleep_time))

                        angle_per_step = (abs_pos_diff / steps_needed) * direction


                        #print("steps needed,angle_per_step:", steps_needed, angle_per_step)

                        for i in range(steps_needed):
                            step_angle = current_pos + (i + 1) * angle_per_step
                            #print(step_angle)
                            self.servos[servo_id]["servo"].angle = step_angle
                            #print(step_angle)
                            await asyncio.sleep(step_sleep_time / 1000 )

                        self.servos[servo_id]["servo"].angle = servo_angle

                        await asyncio.sleep(0.01)

                        return 0


            elif line.upper().startswith("DELAY"):


                if len(line_split) < 2:
                    self.debug("No delay time specified in line: " + line)
                    delay_time = 1000
                else:
                    delay_time = line_split[1]

                delay_time = float(delay_time)

                delay_time = delay_time / 1000

                self.debug("sleeping for: " + str(delay_time))


                await asyncio.sleep(delay_time)

            elif "WAIT" in line.upper():

                do_wait = True
                wait_counter = 0

                while do_wait:
                    print(".....")
                    print(self.actions[script_name])
                    print(len(self.actions[script_name]))
                    if len(self.actions[script_name]) == 1:
                        print("no need to wait anymore")
                        do_wait = False


                    print(wait_counter,self.class_args["MAX_WAIT"])

                    wait_counter += 1
                    if wait_counter > self.class_args["MAX_WAIT"]:
                        do_wait = False

                    if do_wait:
                        await asyncio.sleep(0.25)



            elif line.startswith("R"):
                params = line.split()
                params.pop(0)
                routine = params[0]
                params.pop(0)

                self.debug("executing function: " + routine + " with params: " + str(params))
                await self._execute_function(script,routine,script_name,params)

            elif line.startswith("G"):

                params = line.split()
                params.pop(0)
                if params[0].startswith("S"):
                    pass




