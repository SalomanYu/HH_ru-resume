import sqlite3
import os
from typing import NamedTuple

DATABASE = "shortnames_for_university"
TABLE = "univers2"

class Connection(NamedTuple):
    cursor: sqlite3.Cursor
    db: sqlite3.Connection


class University(NamedTuple):
    fullname: str
    shortname: str
    city: str
    url: str

class JsonUniversity(NamedTuple):
    hh_name: str
    best_choice: str
    similarity: int
    is_current: bool


def connect_to_shortnames_db() -> Connection:
    os.makedirs(name='SQL', exist_ok=True)
    db = sqlite3.connect(f'SQL/{DATABASE}.db')
    cursor = db.cursor()
    return Connection(cursor, db)


# connect_to_db('hello')
def create_shortnames_table() -> None:
    cursor, db = connect_to_shortnames_db()

    pattern = f"""
        CREATE TABLE IF NOT EXISTS {TABLE}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname VARCHAR(255),
            shortname VARCHAR(255),
            city VARCHAR(50),
            url VARCHAR(255)
        )
    """
    cursor.execute(pattern)
    db.commit()
    db.close()


def add_shortnames(data: University) -> None:
    cursor, db = connect_to_shortnames_db()
    pattern = f"""
        INSERT INTO {TABLE}(
            fullname,
            shortname,
            city,
            url
        ) VALUES({','.join('?' for i in range(len(data)))})
    """
    cursor.execute(pattern, data)
    db.commit()
    db.close()
    # logging.info("Added college - %s", data.name)