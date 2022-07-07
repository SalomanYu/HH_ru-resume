import json
import sqlite3
import os

from settings import Connection, ResumeProfessionItem, ResumeGroup


class SelectData:
    def __init__(self, db_path: str, file_output_name: str):
        self.path = db_path
        self.file_output_name = file_output_name

    def collect(self) -> None:
        data = self.select_all_rows()
        groups = self.group_user_ids_to_dict(data)
        self.save_to_json(groups)

        print('Данные были пересены и сгруппированны в json-формате: JSON/' + self.file_output_name)

    def connect_to_db(self, path: str) -> Connection:
        try:
            db = sqlite3.connect(path)
            cursor = db.cursor()
            return Connection(cursor=cursor, db=db)
        except sqlite3.Error as error:
            print(error)
            return None


    def select_all_rows(self) -> list[ResumeProfessionItem]:
        cur = self.connect_to_db(self.path).cursor
        if cur is None:
            return None

        cur.execute('SELECT * FROM resumes')
        resumes = [ResumeProfessionItem(*resume[1:]) for resume in cur.fetchall()] # принести всё
        return resumes

        # data = []
        # resume_num = 0
        # for resume in resumes:
        #     resume_num += 1
        #     data.append({
        #         'id': resume_num,
        #         'user_id(url)': resume.url,
        #         'name_of_profession': resume.name,
        #         'experience_interval': resume.experience_interval,
        #         'experience_duration': resume.experience_duration,
        #         'experience_post': resume.experience_post,
        #         'branch': resume.branch,
        #         'subbranch': resume.subbranch,
        #         'general_experience': resume.general_experience,
        #         'specialization': resume.specialization,
        #         'weight_in_group': resume.weight_in_group,
        #         'level': resume.level,
        #         'weight_in_level': resume.weight_in_level,
        #         'category_name': resume.category,
        #         'city': resume.city,
        #         'salary': resume.salary,
        #         'higher_education_university': resume.university_name,
        #         'higher_education_direction': resume.university_direction,
        #         'higher_education_year': resume.university_year,
        #         'languages': resume.languages,
        #         'skills': resume.skills,
        #         'advanced_training_name': resume.training_name,
        #         'advanced_training_direction': resume.training_direction,
        #         'advanced_training_year': resume.training_year,
        #     })
        # return data

    def group_user_ids_to_dict(self, data: list[ResumeProfessionItem]) -> ResumeGroup:
        groups_dict = {}
        
        # for row in data:
        #     url = row['user_id(url)']
        #     if url in groups_dict:
        #         is_repeat_resume = False
        #         for elem in groups_dict[url]:
        #             if row['experience_interval'] == elem['experience_interval'] and row['experience_post'] == elem['experience_post']:
        #                 is_repeat_resume = True
        #                 break
        #         if not is_repeat_resume:
        #             groups_dict[url].append(row)
            
        #     else:
        #         groups_dict[url] = [row]

        # return groups_dict
        for resume in data:
            url = resume.url
            if url in groups_dict:
                is_repeat_resume = False
                for work in groups_dict[url]:
                    if (work.experience_interval == resume.experience_interval) and (work.experience_post == resume.experience_post):
                        is_repeat_resume = True
                        break
                if not is_repeat_resume:
                    # groups_dict[url].append({
                    # 'user_id(url)': resume.url,
                    # 'name_of_profession': resume.name,
                    # 'experience_interval': resume.experience_interval,
                    # 'experience_duration': resume.experience_duration,
                    # 'experience_post': resume.experience_post,
                    # 'branch': resume.branch,
                    # 'subbranch': resume.subbranch,
                    # 'general_experience': resume.general_experience,
                    # 'specialization': resume.specialization,
                    # 'weight_in_group': resume.weight_in_group,
                    # 'level': resume.level,
                    # 'weight_in_level': resume.weight_in_level,
                    # 'category_name': resume.category,
                    # 'city': resume.city,
                    # 'salary': resume.salary,
                    # 'higher_education_university': resume.university_name,
                    # 'higher_education_direction': resume.university_direction,
                    # 'higher_education_year': resume.university_year,
                    # 'languages': resume.languages,
                    # 'skills': resume.skills,
                    # 'advanced_training_name': resume.training_name,
                    # 'advanced_training_direction': resume.training_direction,
                    # 'advanced_training_year': resume.training_year,
                    # })
                    groups_dict[url].append(resume)
            else:
                # groups_dict[url] = [{
                #     'user_id(url)': resume.url,
                #     'name_of_profession': resume.name,
                #     'experience_interval': resume.experience_interval,
                #     'experience_duration': resume.experience_duration,
                #     'experience_post': resume.experience_post,
                #     'branch': resume.branch,
                #     'subbranch': resume.subbranch,
                #     'general_experience': resume.general_experience,
                #     'specialization': resume.specialization,
                #     'weight_in_group': resume.weight_in_group,
                #     'level': resume.level,
                #     'weight_in_level': resume.weight_in_level,
                #     'category_name': resume.category,
                #     'city': resume.city,
                #     'salary': resume.salary,
                #     'higher_education_university': resume.university_name,
                #     'higher_education_direction': resume.university_direction,
                #     'higher_education_year': resume.university_year,
                #     'languages': resume.languages,
                #     'skills': resume.skills,
                #     'advanced_training_name': resume.training_name,
                #     'advanced_training_direction': resume.training_direction,
                #     'advanced_training_year': resume.training_year,
                # }]       
                groups_dict[url] = [resume] 
        
        return groups_dict

    def save_to_json(self, data):
        

        os.makedirs('JSON', exist_ok=True)

        with open(f'JSON/{self.file_output_name}.json', 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    collector = SelectData(
        db_path='/home/yunoshev/Documents/Edwica/Resumes/result_server/SQL/Professions(2022_6).db',
        file_output_name='step_2_groups_result'
    )
    collector.collect()
