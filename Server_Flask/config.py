import os

class EndConfig():
    DIRECTORY_PATH = ""
    MAP_PATH = DIRECTORY_PATH + ""
    MAP_PROCESSED_PATH = MAP_PATH + ""
    STATUS_PATH = DIRECTORY_PATH + ""
    ALLOWED_MAP_EXTENSIONS = [""]

class LaptopPrototypeConfig():
    DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
    MAP_PATH = os.path.join(os.path.join(DIRECTORY_PATH, "map"), "data")
    MAP_PROCESSED_PATH = os.path.join(DIRECTORY_PATH, "map")
    STATUS_PATH = os.path.join(DIRECTORY_PATH, "status")
    ALLOWED_MAP_EXTENSIONS = ["SLAM"]
