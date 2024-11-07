# database.py
import sqlite3
import os
from datetime import datetime, timedelta

db_dir = os.path.dirname(__file__) + r"\users.db"


def log(data):
    print(f"UPDATE: {data}")


def create():
    con = sqlite3.connect(db_dir)
    with con:
        cur = con.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        tid INTEGER NOT NULL,
        lastplay TEXT
        )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS promocodes (
        promocode TEXT NOT NULL PRIMARY KEY,
        tid INTEGER NOT NULL,
        message_id INTEGER,
        till TEXT,
        discount INTEGER
        )"""
        )
    con.close()
    log(f"database created: {db_dir}")


def add_promocode(tid, promocode, message_id, till, discount):
    con = sqlite3.connect(db_dir)
    with con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO promocodes (promocode, tid, message_id, till, discount) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (promocode, tid, message_id, till, discount),
        )
        cur.execute(
            """
            UPDATE users SET (lastplay) = (?) WHERE tid = ?
            """,
            (datetime.fromisoformat(till) - timedelta(hours=24), tid),
        )
    log(f"new promocode ({promocode}) added in database")
    con.close()


def delete_promocode(promocode):
    con = sqlite3.connect(db_dir)
    with con:
        cur = con.cursor()
        cur.execute("DELETE FROM promocodes WHERE promocode = ?;", (promocode,))
    con.close()
    log(f"promocode ({promocode}) deleted from database")


def get_promocode(promocode):
    con = sqlite3.connect(db_dir)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM promocodes WHERE promocode = ?", (promocode,))
        data = cur.fetchone()
    fields = ["promocode", "tid", "message_id", "till", "discount"]
    con.close()
    if data:
        return dict(zip(fields, data))
    return dict()


def find_promocode(tid):
    con = sqlite3.connect(db_dir)
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM promocodes WHERE tid = ?", (tid,))
        data = cur.fetchone()
    fields = ["promocode", "tid", "message_id", "till", "discount"]
    con.close()
    if data:
        return dict(zip(fields, data))
    return dict()


def get_user(id: int) -> dict:
    con = sqlite3.connect(db_dir)
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM users WHERE tid = ?", (id,))
        data = cur.fetchone()
    fields = ["id", "username", "tid", "lastplay"]
    con.close()
    if data:
        return dict(zip(fields, data))
    return dict()


def create_user(id: int, username: str):
    con = sqlite3.connect(db_dir)
    with con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (username, tid) VALUES (?, ?)",
            (username, id),
        )
    con.close()
    log(f"new user added: id - {id}, username - {username}")


def set_user(id, lastplay=datetime.now()):
    con = sqlite3.connect(db_dir)
    with con:
        cur = con.cursor()
        try:
            lastplay.isoformat()
            flag = True
        except:
            flag = False

        cur.execute(
            "UPDATE users SET (lastplay) = (?) WHERE tid = ?",
            (lastplay.isoformat() if flag else None, id),
        )
        log(f"user ({id}) changed last play time")
    con.close()
