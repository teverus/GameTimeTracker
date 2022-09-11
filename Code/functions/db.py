from sqlite3 import connect
from typing import Union

import pandas as pd
from pandas import DataFrame

from Code.constants import FILES


def get_connection(table_name: str, folder: str):
    return connect(f"{folder + '/' if folder else ''}{table_name}.db")


def create_table(table_name: str, columns: list, folder: str = ""):
    connection = get_connection(table_name, folder)
    df = DataFrame([], columns=columns)
    df.to_sql(f"{table_name}", connection, index=False, if_exists="replace")


def write_to_table(df, table_name, folder: str = ""):
    connection = get_connection(table_name, folder)
    df.to_sql(table_name, connection, index=False, if_exists="replace")


def append_to_table(df: DataFrame, table_name: str, folder: str = ""):
    table = read_table(table_name, folder)
    result = pd.concat([table, df], ignore_index=True)
    write_to_table(result, table_name, folder)


def update_a_table(
    x_column: str,
    x_value: Union[str, int],
    y_column: str,
    new_value: Union[str, int],
    table_name: str,
    folder: str,
):
    df = read_table(table_name, folder)

    index = list(df.loc[df[x_column] == x_value].index)
    assert len(index) == 1, "\n[ERROR] More than 1 index was found"
    row_index = index[0]
    column_index = df.columns.get_loc(y_column)
    df.iloc[row_index, column_index] = new_value

    write_to_table(df, table_name, folder)


def read_table(table_name, folder: str = "") -> DataFrame:
    connection = get_connection(table_name, folder)
    return pd.read_sql(f"select * from {table_name}", connection)


def append_row_to_table(df_content: list, df_columns: list, table_name: str):
    df = DataFrame([], columns=df_columns)
    df.loc[0] = df_content

    if int(df.ID) not in set(read_table(table_name, FILES).ID):
        append_to_table(df, table_name, FILES)


def read_a_table(table_name):
    return read_table(table_name, FILES)
