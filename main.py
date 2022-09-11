from time import sleep

import psutil
from datetime import datetime as dt

APP_NAME = "Notepad"
APP_PROCESS = "notepad.exe"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Application:
    def __init__(self):
        self.timeout = 1
        self.database = {}
        self.process_is_active = False

        while True:

            if self.check_if_process_exists(APP_PROCESS):
                if not self.process_is_active:
                    self.database[APP_NAME] = {}
                    self.database[APP_NAME]["start"] = self.get_time()
                    self.process_is_active = True

            else:
                if self.process_is_active:
                    self.database[APP_NAME]["finnish"] = self.get_time()
                    self.process_is_active = False

            sleep(self.timeout)

    @staticmethod
    def check_if_process_exists(process_name):
        for p in psutil.process_iter():
            if p.name() == process_name:
                return True

    @staticmethod
    def get_time(time_format=TIME_FORMAT):
        return dt.now().strftime(time_format)


if __name__ == "__main__":
    Application()
