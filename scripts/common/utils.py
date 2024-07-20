from typing import TypedDict
from datetime import datetime

import psycopg2


class DBConfigs(TypedDict):
    LL_DB_HOST: str
    LL_DB_PORT: str
    LL_DB_NAME: str
    LL_DB_USER: str
    LL_DB_USER_PSW: str


def get_connection(configs: DBConfigs):
    connection = psycopg2.connect(
        host=configs["LL_DB_HOST"],
        port=configs["LL_DB_PORT"],
        database=configs["LL_DB_NAME"],
        user=configs["LL_DB_USER"],
        password=configs["LL_DB_USER_PSW"],
    )
    return connection


def execute_sql(query, connection):
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


def get_current_utc_time():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
