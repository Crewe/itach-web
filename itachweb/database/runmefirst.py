from database.database import create_connection, sql_exec
from config.config import database_path
from logger.logger import syslog


def initialize_database(drop=False):
    sql_drop_tables = """
    DROP TABLE IF EXISTS port_states;
    DROP TABLE IF EXISTS devices;
    """

    sql_create_devices_table = """
    CREATE TABLE IF NOT EXISTS devices (
    id integer PRIMARY KEY,
    name text NOT NULL,
    date_added text NOT NULL
    );"""

    sql_create_state_table = """
    CREATE TABLE IF NOT EXISTS port_states (
    id integer PRIMARY KEY,
    name text NOT NULL,
    priority integer,
    device_id integer NOT NULL,
    module_id integer NOT NULL,
    port_id integer NOT NULL,
    port_state text NOT NULL,
    last_changed text NOT NULL,
    FOREIGN KEY (device_id) REFERENCES devices (id)
    );"""

    conn = create_connection(database_path())
    if conn is not None:
        if drop:
            syslog().info("Droping all tables")
            sql_exec(conn, sql_drop_tables)
        syslog().info("Creating devices table.")
        sql_exec(conn, sql_create_devices_table)
        syslog().info("Creating device state table.")
        sql_exec(conn, sql_create_state_table)
    else:
        syslog().error("Unable to create database connection.")
