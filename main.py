import os
from datetime import datetime as dt
from datetime import timedelta
from time import sleep

import psutil
import yaml
from pandas import DataFrame

from Code.BaseTable import BaseTable, ColumnWidth
from Code.constants import (
    Column,
    GAME_TIME,
    FILES,
    TIME_FORMAT,
    PROCESS_IS_ACTIVE,
    START,
    FINISH,
    NAME,
    PROCESS,
    LAST_START,
    LAST_FINISH,
    TOTAL,
    SETTINGS,
    APPLICATIONS,
    TABLE_TITLE,
    POLLING_TIMEOUT,
    STUB,
)
from Code.functions.db import append_to_table, update_a_table, read_table


class Application:
    def __init__(self):
        os.system("cls")

        self.config = self.get_config()
        self.settings = self.config[SETTINGS]
        apps = self.config[APPLICATIONS]
        self.applications = STUB if apps is None else apps

        self.df = read_table(GAME_TIME, FILES)
        self.info = {
            application: {LAST_START: "", LAST_FINISH: "", PROCESS_IS_ACTIVE: False}
            for application in sorted([a[NAME] for a in self.applications])
        }
        self.table = None

        self.show_application_stats()
        self.start_tracking_applications()

    def show_application_stats(self):

        self.get_total_time_for_all_games()
        self.get_last_start_and_finish_time_for_each_game()

        r = [[k, v[TOTAL], v[LAST_START], v[LAST_FINISH]] for k, v in self.info.items()]

        self.table = BaseTable(
            table_title=self.settings[TABLE_TITLE],
            headers=["Name", "Total time", "Last start", "Last finish"],
            rows=r,
            rows_top_border="-",
            column_widths={
                0: ColumnWidth.FULL,
                1: ColumnWidth.FIT,
                2: ColumnWidth.FIT,
                3: ColumnWidth.FIT,
            },
        )
        self.table.print_table()

    def start_tracking_applications(self):
        total = 1
        start = 2
        finish = 3

        while True:

            for i, application in enumerate(self.applications):
                app_name = application[NAME]
                app_process = application[PROCESS]
                process_exists = bool(self.check_if_process_exists(app_process))
                is_active = self.info[app_name][PROCESS_IS_ACTIVE]

                if process_exists and not is_active:
                    self.info[app_name][START] = self.get_time()
                    self.record_app_name_and_start_time(app_name)

                    self.info[app_name][PROCESS_IS_ACTIVE] = True

                    self.table.rows_raw[i][start] = self.info[app_name][START]
                    self.table.rows_raw[i][finish] = " "
                    self.table.highlight.append([i, 0])

                    self.table.print_table()

                elif not process_exists and is_active:
                    self.info[app_name][FINISH] = self.get_time()
                    self.record_finish_time(app_name)
                    self.record_time_spent(app_name)

                    self.info[app_name][PROCESS_IS_ACTIVE] = False

                    self.table.rows_raw[i][finish] = self.info[app_name][FINISH]
                    total_time = self.get_total_time_for_a_single_game(app_name)
                    self.table.rows_raw[i][total] = total_time
                    self.table.highlight.remove([i, 0])

                    self.table.print_table()

                sleep(self.settings[POLLING_TIMEOUT])

    @staticmethod
    def check_if_process_exists(process_name):
        for p in psutil.process_iter():
            if p.name() == process_name:
                return True

    @staticmethod
    def get_time(time_format=TIME_FORMAT):
        return dt.now().strftime(time_format)

    def record_app_name_and_start_time(self, app_name):
        df = DataFrame([], columns=Column.ALL)
        df.loc[0, Column.NAME] = app_name
        df.loc[0, Column.START] = self.info[app_name][START]
        append_to_table(df, GAME_TIME, FILES)

    def record_finish_time(self, app_name):
        update_a_table(
            x_column=Column.START,
            x_value=self.info[app_name][START],
            y_column=Column.FINISH,
            new_value=self.info[app_name][FINISH],
            table_name=GAME_TIME,
            folder=FILES,
        )

    def record_time_spent(self, app_name):
        time_start = dt.strptime(self.info[app_name][START], TIME_FORMAT)
        time_finish = dt.strptime(self.info[app_name][FINISH], TIME_FORMAT)
        time_spend = str(time_finish - time_start)

        update_a_table(
            x_column=Column.START,
            x_value=self.info[app_name][START],
            y_column=Column.SPENT,
            new_value=time_spend,
            table_name=GAME_TIME,
            folder=FILES,
        )

    @staticmethod
    def get_time_in_seconds(time_as_string):
        try:
            time = dt.strptime(time_as_string, "%H:%M:%S")
            delta = timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)

            return int(delta.total_seconds())

        except TypeError:
            return 0

    def get_total_time_for_all_games(self):
        for application in self.applications:
            app_name = application[NAME]
            total_time = self.get_total_time_for_a_single_game(app_name)

            self.info[app_name][TOTAL] = total_time

    def get_total_time_for_a_single_game(self, app_name):
        df = read_table(GAME_TIME, FILES)

        time_spent_stats = df.loc[df.Name == app_name].Spent
        time_spent = sum([self.get_time_in_seconds(t) for t in time_spent_stats])
        hours = int(time_spent / 3600)
        minutes = int((time_spent - (hours * 3600)) / 60)
        seconds = time_spent - (hours * 3600) - (minutes * 60)

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def get_last_start_and_finish_time_for_each_game(self):
        for application in self.info:
            try:
                last_start = self.df.loc[self.df.Name == application].Start.values[-1]
                last_finish = self.df.loc[self.df.Name == application].Finish.values[-1]
            except IndexError:
                last_start = "---"
                last_finish = "---"

            last_finish = "error" if not last_finish else last_finish

            self.info[application][LAST_START] = last_start
            self.info[application][LAST_FINISH] = last_finish

    @staticmethod
    def get_config():
        with open("config.yml", "r") as stream:
            return yaml.safe_load(stream)


if __name__ == "__main__":
    Application()
