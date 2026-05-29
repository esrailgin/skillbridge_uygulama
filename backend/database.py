import os
from contextlib import contextmanager

import pyodbc


DEFAULT_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-081C6NO\\SQLEXPRESS02;"
    "DATABASE=SkillBridge;"
    "Trusted_Connection=yes;"
)


def get_connection_string() -> str:
    return os.getenv("SKILLBRIDGE_DB_CONNECTION", DEFAULT_CONNECTION_STRING)


def get_db():
    return pyodbc.connect(get_connection_string())


@contextmanager
def db_cursor(commit: bool = False):
    conn = get_db()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        if commit:
            conn.rollback()
        raise
    finally:
        conn.close()