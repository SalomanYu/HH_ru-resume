"""Основной файл, который будет вызывать этапы построения траектории один за другим"""

import os
from rich.console import Console
from rich.progress import track

import settings
from steps.step_1_parse_current_profession import ProfessionParser
from steps.step_2_collected_data import SelectData
from steps.step_3_remove_repeat_groupes import filtering_groups, remove_dublicates
from steps.step_4_rename_to_default_name import rename_resumes
from steps.step_5_join_reset_steps_in_career import JoinDublicateSteps
from steps.step_6_detect_profession_experience_time import change_level_for_zero_positions, detect_experience, save_update_zero_professions


class Trajectory:
    def __init__(self, professions_db: str, logging_dir: str):
        self.professions_db = professions_db
        self.logging_dir = logging_dir
        self.db_table_name = "Медицина_и_здоровье"

    def parse_current_profession(self) -> None:
        log = settings.start_logging(logfile="step_1.log", folder=self.logging_dir)
        excel_data = settings.connect_to_excel(path=self.professions_db)
        console.log("[green] Start parsing professions")
        for item in track(range(len(excel_data.names)), description="[yellow]HH.ru parser progress"):
            log.debug("Searching profession - %s", excel_data.names[item])
            
            self.db_table_name = excel_data.area
            profession = ProfessionParser(
                name_db_table=self.db_table_name,
                profession_name=excel_data.names[item],
                profession_area=excel_data.area,
                profession_level=excel_data.levels[item],
                profession_weight_in_group=excel_data.weights_in_group[item],
                profession_weight_in_level=excel_data.weights_in_level[item]
            )
            profession.find()

    def collect_data_from_sql_to_json(self) -> None:
        log = settings.start_logging(logfile="step_2.log", folder=self.logging_dir)
        collector = SelectData(
            db_path=os.path.join("SQL", settings.CURRENT_MONTH, settings.DATABASE_NAME),
            db_table=self.db_table_name,
            file_output_name="", # переменная
            log=log
        )
        collector.collect()
    
    def remove_repeat_groupes(self):
        log = settings.start_logging(logfile="step_3.log", folder=self.logging_dir)
        data = settings.load_resumes_json(log, path=settings.STEP_2_JSON_FILE) # можно тоже заменить на меременную название файла
        groups, duplicate_list = filtering_groups(log, data)
        retranseld_dict = settings.nested_tuple_to_dict(nested_tuple=groups)
        data_without_duplicates = remove_dublicates(log=log, data=retranseld_dict, list_to_delete=duplicate_list)
        settings.save_to_json(log, data=data_without_duplicates, filename=settings.STEP_3_JSON_FILE)

    def rename_to_default_names(self):
        log = settings.start_logging("step_4.log", folder=self.logging_dir)
        rename_resumes(log)

    
    def join_reset_steps(self):
        log = settings.start_logging("step_5.log", folder=self.logging_dir)
        join_step = JoinDublicateSteps()
        join_step.start(log)
    
    def detect_profession_experience_time(self):
        log = settings.start_logging("step_6.log", folder=self.logging_dir)
        data = settings.load_resumes_json(log, path=settings.STEP_5_JSON_FILE)
        dict_with_experience_statistic = detect_experience(data)
        updated_zero_professions = change_level_for_zero_positions(dict_with_experience_statistic)
        save_update_zero_professions(log, updated_zero_professions, data)

    def step_7(self):
        pass    

    def step_8(self):
        pass
    

def create_trajectory(professions_path: str):
    trajectory = Trajectory(professions_db=os.path.join(settings.PROFESSIONS_FOLDER_PATH, professions_path), logging_dir=ex_file.replace(".xlsx", ''))
    trajectory.parse_current_profession()
    # trajectory.collect_data_from_sql_to_json()
    # trajectory.remove_repeat_groupes()
    # trajectory.rename_to_default_names()
    # trajectory.join_reset_steps()
    # trajectory.detect_profession_experience_time()


if __name__ == "__main__":
    console = Console()

    for ex_file in os.listdir(path=settings.PROFESSIONS_FOLDER_PATH):
        if ex_file.endswith(".xlsx"):
            if ex_file == "43 Маркетинг _ Реклама. _ PR.xlsx":
                create_trajectory(professions_path=ex_file)
                # break
    