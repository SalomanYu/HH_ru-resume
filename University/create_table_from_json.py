import sqlite3
import json
import os

from rich.progress import track
from rich.console import Console

from database import DATABASE, JsonUniversity, University, Connection

TABLE = "univers"
DATABASE = "finalResult"

console = Console()


def connect_to_db() -> Connection:
    os.makedirs(name='SQL', exist_ok=True)
    db = sqlite3.connect(f'SQL/{DATABASE}.db')
    cursor = db.cursor()
    return Connection(cursor, db)


# connect_to_db('hello')
def create_table() -> None:
    cursor, db = connect_to_db()

    pattern = f"""
        CREATE TABLE IF NOT EXISTS {TABLE}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname VARCHAR(255),
            shortname VARCHAR(255),
            city VARCHAR(50)
        )
    """
    cursor.execute(pattern)
    db.commit()
    db.close()


def add(data: University) -> None:
    cursor, db = connect_to_db()
    pattern = f"""
        INSERT INTO {TABLE}(
            fullname,
            shortname,
            city
        ) VALUES({','.join('?' for i in range(len(data)))})
    """
    cursor.execute(pattern, data)
    db.commit()
    db.close()



def get_data_from_sql(dbname: str, table: str) -> list[University]:
    cursor = sqlite3.connect(dbname).cursor()
    data =  cursor.execute(f"SELECT * FROM {table}").fetchall()
    console.log("[green] GET data from SQL")
    return [University(*row[1:]) for row in data] #row[1:] чтобы не трогать  id


def get_data_from_json() -> list[JsonUniversity]:
    data = json.load(open("result.json", "r"))
    res = []
    for item in data:
        json_university = JsonUniversity(*item.values())
        res.append(json_university)
    console.log("[green] GET data from JSON")
    return res


if __name__ == "__main__":
    create_table()

    json_univers = get_data_from_json()
    current_univers = get_data_from_sql("/home/yunoshev/shortnames_for_university.db", "univers2")

    console.log("[blue] Start matching univers")
    for j_univer in track(range(len(json_univers)), description="[yellow]ProgressBar"):
        j_univer = json_univers[j_univer]
        if j_univer.is_current: 
            for c_univer in current_univers:
                if c_univer.fullname == j_univer.best_choice:
                    add(University(fullname=j_univer.best_choice, shortname=c_univer.shortname, city=c_univer.city, url="")[:-1]) # Не записываем ссылку
        else:
            # console.log("[red] Find incorrect university match")
            add(University(fullname=j_univer.hh_name, shortname="", city="", url="")[:-1]) # Не записываем ссылку
    console.log("[green] Finished")
    