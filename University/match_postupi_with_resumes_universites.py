import json
from fuzzywuzzy import process
import sqlite3

from rich.progress import track

from database import JsonUniversity


def get_univers_from_resumes() -> list:
    cursor = sqlite3.connect("/home/yunoshev/Documents/Edwica/Resumes/result_server/SQL/Professions(2022_6).db").cursor()
    univers = cursor.execute("SELECT higher_education_university FROM resumes").fetchall()
    formated_univers = []
    for row in univers:
        for univer in row[0].split("|"):
            formated_univers.append(univer)
    return formated_univers

def get_univers_from_postupi_online() -> list:
    cursor = sqlite3.connect("SQL/shortnames_for_university.db").cursor()
    univers = cursor.execute("SELECT fullname FROM univers2").fetchall()
    return [univer[0] for univer in univers] # univer[0] потому что fetchall возвращает кортеж


def main():
    data = []
    univers_hh = get_univers_from_resumes()
    correct_univers = get_univers_from_postupi_online()

    for univer in track(range(len(univers_hh)), description="[green]ProgressBar"):
        hh_univer = univers_hh[univer].split(',')[0].strip().lower() # Вырезаем города, указанные после запятой
        best_choice, similarity = process.extractOne(query=hh_univer, choices=correct_univers)
        if similarity > 88:
            json_univer = JsonUniversity(hh_univer, best_choice, similarity, True)
            if data:
                resume_univers_in_data = [item['university_resume'] for item in data]
                if hh_univer.capitalize() not in resume_univers_in_data:
                    data.append({
                        "university_resume": json_univer.hh_name.capitalize(),
                        "best_choice": json_univer.best_choice,
                        "similarity": json_univer.similarity,
                        "is_current": json_univer.is_current # можно потом вручную исправить в готовом json файле
                    })
            else:
                data.append({
                    "university_resume": json_univer.hh_name.capitalize(),
                    "best_choice": json_univer.best_choice,
                    "similarity": json_univer.similarity,
                    "is_current": json_univer.is_current # можно потом вручную исправить в готовом json файле
                })

    with open("result.json", "w") as file:
        json.dump(list(data), file, ensure_ascii=False, indent=2)    


if __name__ == "__main__":
    answer = input("Перезаписать уже существующий и отредактированный файл? (y/n)\n>>> ")
    if answer == "y":
        main()
    exit("Finished.")
