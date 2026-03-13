import os
from dotenv import load_dotenv
from datetime import datetime

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
import pytz

load_dotenv()


def _env(name, default=None, required=False):
    value = os.getenv(name, default)
    if isinstance(value, str):
        value = value.strip()
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _boolEnv(name, default=False):
    value = str(_env(name, str(default))).lower()
    return value in {"1", "true", "yes", "on"}


def _poolConfig():
    config = {
        "pool_name": "grungaPool",
        "pool_size": int(_env("DB_POOL_SIZE", "8")),
        "host": _env("DB_HOST", required=True),
        "port": int(_env("DB_PORT", "3306")),
        "user": _env("DB_USER", required=True),
        "password": _env("DB_PASS", required=True),
        "database": _env("DB_NAME", required=True),
        "autocommit": False,
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci",
        "ssl_disabled": _boolEnv("DB_SSL_DISABLED", False),
    }

    sslCa = _env("DB_SSL_CA")
    if sslCa:
        config["ssl_ca"] = sslCa

    sslCert = _env("DB_SSL_CERT")
    if sslCert:
        config["ssl_cert"] = sslCert

    sslKey = _env("DB_SSL_KEY")
    if sslKey:
        config["ssl_key"] = sslKey

    return config


POOL = MySQLConnectionPool(**_poolConfig())


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
