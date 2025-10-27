import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

@contextmanager
def db_cursor(commit=False):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        yield cur
        if commit:
            conn.commit()
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()
