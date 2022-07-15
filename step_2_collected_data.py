import json
import sqlite3
import os

from settings import Connection, ResumeProfessionItem, ResumeGroup, start_logging


class SelectData:
    def __init__(self, db_path: str, file_output_name: str):
        self.path = db_path
        self.file_output_name = file_output_name

    def collect(self) -> None:
        """Основной метод, который запускает все остальные функции"""
        data = self.select_all_rows()
        groups = self.group_user_ids_to_dict(data)
        self.save_to_json(groups)
        log.info("Complete!")

    def connect_to_db(self, path: str) -> Connection:
        try:
            if not os.path.exists(path):
                raise FileExistsError

            db = sqlite3.connect(path)
            cursor = db.cursor()
            log.info("Successfully connected to Database: %s", path)
            return Connection(cursor=cursor, db=db)

        except sqlite3.Error as error:
            log.error("Failed connecting to Database: %s", path)
            log.error("Error message: %s", error)
            exit("Failed connecting to Database")
        
        except FileExistsError:
            log.error("Database None-exists! %s", path)
            exit("Database None-exists!")


    def select_all_rows(self) -> list[ResumeProfessionItem]:
        cur = self.connect_to_db(self.path).cursor
        cur.execute('SELECT * FROM resumes')

        fields = [
            'weight_in_group', 'level', 'level_in_group', 'name_of_profession', 'category_resume', 'city', 'general_experience', 'specialization',
            'salary', 'higher_education_university', 'higher_education_direction', 'higher_education_year', 'languages', 'skills', 'advanced_training_name',
            'advanced_training_direction', 'advanced_training_year', 'branch', 'subbranch', 'experience_interval', 'experience_duration', 'experience_post', 'user_id(url)']
        resumes = [dict(zip(fields, resume[1:])) for resume in cur.fetchall()] # [1:] чтобы не брать айди
        
        return resumes
        

    def group_user_ids_to_dict(self, data: list[ResumeProfessionItem]) -> ResumeGroup:
        groups_dict = {}
        for row in data:
            url = row['user_id(url)']
            if url in groups_dict:
                is_repeat_resume = False
                for elem in groups_dict[url]:
                    if row['experience_interval'] == elem['experience_interval'] and row['experience_post'] == elem['experience_post']:
                        print("fdsfsdfds")
                        is_repeat_resume = True
                        break
                if not is_repeat_resume:
                    groups_dict[url].append(row)

            else:
                groups_dict[url] = [row]
        return groups_dict


    def save_to_json(self, data: list[dict]) -> None:
        os.makedirs('JSON', exist_ok=True)
        with open(f'JSON/{self.file_output_name}.json', 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=2) 


if __name__ == "__main__":
    log = start_logging(logfile="step_2.log")
    collector = SelectData(
        db_path='/home/yunoshev/Documents/Edwica/Resumes/result_server/SQL/(2022_6).db',
        file_output_name='step_2_groups_result'
    )
    collector.collect()
