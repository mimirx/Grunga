import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from datetime import datetime
import pytz
from contextlib import contextmanager

load_dotenv()

POOL = MySQLConnectionPool(
    pool_name="grungaPool",
    pool_size=int(os.getenv("DB_POOL_SIZE", "8")),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME"),
    autocommit=False,
    charset="utf8mb4",
    collation="utf8mb4_unicode_ci",
)

def _chicagoOffset():
    tz = pytz.timezone("America/Chicago")
    nowCt = datetime.now(tz)
    off = nowCt.utcoffset()
    totalMinutes = int(off.total_seconds() // 60)
    sign = '+' if totalMinutes >= 0 else '-'
    h = abs(totalMinutes) // 60
    m = abs(totalMinutes) % 60
    return f"{sign}{h:02d}:{m:02d}"

def getConnection():
    conn = POOL.get_connection()
    cur = conn.cursor()
    cur.execute(f"SET time_zone = '{_chicagoOffset()}'")
    cur.execute("SET sql_safe_updates = 0")
    cur.close()
    return conn

class Db:
    def __init__(self, commit=False):
        self.commit = commit
        self.conn = None
        self.cur = None
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
    def __exit__(self, excType, exc, tb):
        if excType is None:
            if self.commit:
                self.conn.commit()
        else:
            self.conn.rollback()
        try:
            self.cur.close()
        finally:
            self.conn.close()

def db_cursor(commit=False):
    return Db(commit=commit)

def fetchAll(sql, params=None):
    with Db() as db:
        db.execute(sql, params)
        return db.fetchAll()

def fetchOne(sql, params=None):
    with Db() as db:
        db.execute(sql, params)
        return db.fetchOne()

def execute(sql, params=None):
    with Db(commit=True) as db:
        db.execute(sql, params)
        return dict(lastRowId=db.lastRowId(), rowCount=db.rowCount())
