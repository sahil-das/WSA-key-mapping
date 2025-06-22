from adb_helper import auto_connect_wsa
from input_listeners import start_listeners
from gui import create_controller

if __name__ == "__main__":
    auto_connect_wsa()
    start_listeners()
    create_controller()
