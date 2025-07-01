
import os
import asyncio

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






    def __init__(self,**kwargs):


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




    def read_script(self,script_name):

        config = open(self.scripts[script_name],"r").read()

        sections = { }

        section = "na"

        for line in config.split("\n"):
            if line.strip() == "":
                continue
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





