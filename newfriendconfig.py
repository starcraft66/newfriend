import json

class Configuration(object):

    def __init__(self, path):
        try:
            with open(path, 'r') as f:
                config = json.load(f)
                if config:
                    self.port = config["port"]
                    self.frontend = config["frontend"]
                    self.nbt_file_path = config["nbt_file_path"]
                else:
                    print("error reading config")
                    exit(1)
        except IOError:
            print("error reading config")
            exit(1)