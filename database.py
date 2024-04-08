import sqlite3
from sqlite3 import Error
from logger import syslog


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        syslog().info(f"Successfully connected sqlite version {sqlite3.version}")
        return conn
    except Error as e:
        syslog().error("Unable to connect to database.")
    return conn


def sql_exec(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        syslog().error("Unable to execute query.")
        syslog().debug(e)
