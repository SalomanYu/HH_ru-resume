import json
import os
import sqlite3
from dataclasses import dataclass
import sys


INPUT_DATABASE = '/home/yunoshev/Documents/Edwica/Resumes/result_server/SQL/Month:6.2022/Professions.db'
TABLE_NAME = "Accountment"


@dataclass(frozen=True, slots=True)
class Connection:
    db: sqlite3.Connection
    cursor: sqlite3.Cursor


def connect_to_db(db_name: str) -> Connection:
    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    return Connection(db, cursor)

def save_json(data: dict):
    with open('res.json', 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print('Saved json!')

def create_json_from_sql():
    cursor = connect_to_db(db_name=INPUT_DATABASE).cursor
    urls = (item[0] for item in cursor.execute(f"SELECT url FROM {TABLE_NAME}").fetchall())
    univers = (item[0] for item in cursor.execute(f"SELECT higher_education_university FROM {TABLE_NAME}").fetchall())
    cities = (item.split(',')[-1] for item in univers)
    for i in cities:
        print(i)
    # result = dict(zip(urls, univers)) #item[0] делает из ('Московский экономико-финансовый институт, Москва',) -> 'Московский экономико-финансовый институт, Москва'
    result = []
    # for item in range(10):
    #     result.append({
    #         "url": urls[item],
    #         "univer": univers[item],
    #         "city": univers[item].split(",")[-1]
    #     })
    # save_json(result)



if __name__ == "__main__":
    create_json_from_sql()