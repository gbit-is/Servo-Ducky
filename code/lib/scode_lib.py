
import os

class scode_reader():


    def __init__(self,script_dir="/scripts"):

        try:
            os.stat(script_dir)
        except Exception as e:
            print("Unable to find script dir")
            print("Exception is:")
            print(e)
            raise Exception()

        if not script_dir.endswith("/"):
            script_dir += "/"

        self.script_dir = script_dir


        self._list_scripts()




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

        all_files = os.listdir(self.script_dir)
        scode_files = { }
        for file in all_files:
            if not file.startswith("."):
                if file.endswith(".scode"):
                    full_path = self.script_dir + file
                    script_name = file.split(".scode")[0]
                    scode_files[script_name] = full_path

        self.scripts = scode_files




