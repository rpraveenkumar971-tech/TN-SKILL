import sqlite3

from .config import DATABASE_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE NOT NULL,

    email TEXT UNIQUE NOT NULL,

    full_name TEXT,

    password_hash TEXT NOT NULL,

    created_at TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT NOT NULL,

    token TEXT UNIQUE NOT NULL,

    login_time TEXT NOT NULL,

    last_activity TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS recommendations (
    id TEXT PRIMARY KEY,

    username TEXT NOT NULL,

    recommendation_type TEXT NOT NULL,

    timestamp TEXT NOT NULL,

    input_json TEXT NOT NULL,

    result_json TEXT NOT NULL,

    result_summary TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT NOT NULL,

    filename TEXT NOT NULL,

    path TEXT NOT NULL,

    created_at TEXT NOT NULL
);
"""


def get_conn():
    """
    Create a SQLite connection.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        str(DATABASE_PATH)
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def init_db():
    """
    Create all required database tables.
    """

    with get_conn() as connection:
        connection.executescript(SCHEMA)

        connection.commit()


def fetch_one(query, params=()):
    """
    Execute SELECT and return one row.
    """

    with get_conn() as connection:
        return connection.execute(
            query,
            params
        ).fetchone()


def fetch_all(query, params=()):
    """
    Execute SELECT and return all rows.
    """

    with get_conn() as connection:
        return connection.execute(
            query,
            params
        ).fetchall()


def execute(query, params=()):
    """
    Execute INSERT / UPDATE / DELETE.
    """

    with get_conn() as connection:

        cursor = connection.execute(
            query,
            params
        )

        connection.commit()

        return cursor.lastrowid