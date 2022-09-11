from datetime import datetime as dt
from time import sleep

import psutil
from pandas import DataFrame

from Code.constants import Column, GAME_TIME, FILES
from Code.functions.db import append_to_table, update_a_table

APP_NAME = "Notepad"
APP_PROCESS = "notepad.exe"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Application:
    def __init__(self):
        self.polling_timeout = 1
        self.process_is_active = False
        self.start_time = None
        self.finish_time = None

        while True:

            if self.check_if_process_exists(APP_PROCESS):
                if not self.process_is_active:
                    self.start_time = self.get_time()

                    df = DataFrame([], columns=Column.ALL)
                    df.loc[0, Column.NAME] = APP_NAME
                    df.loc[0, Column.START] = self.start_time
                    append_to_table(df, GAME_TIME, FILES)

                    self.process_is_active = True

            else:
                if self.process_is_active:
                    self.finish_time = self.get_time()

                    update_a_table(
                        x_column=Column.START,
                        x_value=self.start_time,
                        y_column=Column.FINISH,
                        new_value=self.finish_time,
                        table_name=GAME_TIME,
                        folder=FILES,
                    )

                    time_start = dt.strptime(self.start_time, TIME_FORMAT)
                    time_finish = dt.strptime(self.finish_time, TIME_FORMAT)
                    time_spend = str(time_finish - time_start)

                    update_a_table(
                        x_column=Column.START,
                        x_value=self.start_time,
                        y_column=Column.SPENT,
                        new_value=time_spend,
                        table_name=GAME_TIME,
                        folder=FILES
                    )

                    self.process_is_active = False

            sleep(self.polling_timeout)

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
