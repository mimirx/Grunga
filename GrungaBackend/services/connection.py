import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

load_dotenv()

POOL = MySQLConnectionPool(
    pool_name="grungaPool",
    pool_size=int(os.getenv("DB_POOL_SIZE", "8")),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME"),
    autocommit=False
)

def getConnection():
    conn = POOL.get_connection()
    cur = conn.cursor()
    cur.execute("SET time_zone = '+00:00'")
    cur.execute("SET sql_safe_updates = 0")
    cur.close()
    return conn

class Db:
    def __enter__(self):
        self.conn = getConnection()
        self.cur = self.conn.cursor(dictionary=True)
        return self
    def execute(self, sql, params=None):
        self.cur.execute(sql, params or ())
        return self.cur
    def executemany(self, sql, seq):
        self.cur.executemany(sql, seq)
        return self.cur
    def fetchAll(self):
        return self.cur.fetchall()
    def fetchOne(self):
        return self.cur.fetchone()
    def lastRowId(self):
        return self.cur.lastrowid
    def rowCount(self):
        return self.cur.rowcount
    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.cur.close()
        self.conn.close()

def fetchAll(sql, params=None):
    with Db() as db:
        db.execute(sql, params)
        return db.fetchAll()

def fetchOne(sql, params=None):
    with Db() as db:
        db.execute(sql, params)
        return db.fetchOne()

def execute(sql, params=None):
    with Db() as db:
        db.execute(sql, params)
        return dict(lastRowId=db.lastRowId(), rowCount=db.rowCount())

def executeMany(sql, seq):
    with Db() as db:
        db.executemany(sql, seq)
        return dict(rowCount=db.rowCount())

def get_connection():
    return getConnection()

from contextlib import contextmanager
@contextmanager
def db_cursor(commit=False):
    conn = None
    cur = None
    try:
        conn = getConnection()
        cur = conn.cursor(dictionary=True)
        yield cur
        if commit:
            conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()
