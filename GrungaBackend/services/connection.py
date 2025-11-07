import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from datetime import datetime
import pytz   # <-- make sure pytz is installed (pip install pytz)

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

def _chicago_offset():
    tz = pytz.timezone("America/Chicago")
    now_ct = datetime.now(tz)
    off = now_ct.utcoffset()  # timedelta
    # off can be negative; format ±HH:MM
    total_minutes = int(off.total_seconds() // 60)
    sign = '+' if total_minutes >= 0 else '-'
    h = abs(total_minutes) // 60
    m = abs(total_minutes) % 60
    return f"{sign}{h:02d}:{m:02d}"

def getConnection():
    conn = POOL.get_connection()
    cur = conn.cursor()
    # Use current offset instead of named zone, so no tz tables needed
    cur.execute(f"SET time_zone = '{_chicago_offset()}'")
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
