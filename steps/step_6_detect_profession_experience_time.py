"""
Нам нужно определить средний профессиональный опыт с которым кандидат может претендовать на должность (Junior, Middle, Senior) уровней.
"""

import logging
import settings

from .step_4_rename_to_default_name import get_default_names
from how_time_is_required_for import experience_to_months


def detect_experience(data:dict) -> dict:
    default_names = get_default_names('Маркетинг, реклама, PR')[0]
    resumes = list(data.items())

    time_required_for_levels = {}
    for def_level_name in list(default_names.values()):
        time_required_for_levels[def_level_name] = []
        for resume in resumes:
            if resume[1][0]['name_of_profession'] == def_level_name:
                time_required_for_levels[def_level_name].append(
                    {
                    'user_id': resume[0],
                    'months': experience_to_months(resume[1][0]['general_experience'])
                    })

            else:
                step_position = -1
                job_steps = resume[1][::-1]    
                for step_index in range(len(job_steps)):
                    if job_steps[step_index]['experience_post'] == def_level_name:
                        step_position = step_index
                if step_position == 0 and def_level_name != resume[1][0]['name_of_profession']: # Если в самом начале этап этого уровня
                    time_required_for_levels[def_level_name].append(
                        {
                        'user_id': resume[0],
                        'months': 0
                        })
                    
                elif step_position > 0:
                    level_months = 0
                    for item in range(step_position):
                        level_months += experience_to_months(job_steps[item]['experience_duration'])
                    time_required_for_levels[def_level_name].append(
                        {
                        'user_id': resume[0],
                        'months': level_months
                        })
    return time_required_for_levels     



def change_level_for_zero_positions(data:dict) -> tuple:
    # Нужно поменять этот блок, когда будем проверять выборку больше, чем product manager
    zero_position = tuple(data.items())[0]
    level_groups = tuple(data.items())[1:]
    for zero_item in range(len(zero_position[1])):
        for level in range(len(level_groups)):
            level_sum = 0
            for item in level_groups[level][1]:
                level_sum += item['months']
            average = level_sum // len(level_groups[level][1])
            if (average >= zero_position[1][zero_item]['months']) or (average <= zero_position[1][zero_item]['months'] and level == len(level_groups)-1):
                zero_position[1][zero_item]['new_level'] = level+1
                zero_position[1][zero_item]['new_name'] = level_groups[level][0]
                break
    return zero_position


def save_update_zero_professions(log:logging, zero_professions:dict, original_data:dict) -> dict:
    for profession in zero_professions[1]:
        if profession['user_id'] in original_data:
            for job_step in original_data[profession['user_id']]:
                try:
                    job_step['level'] = profession['new_level']
                    job_step['name_of_profession'] = profession['new_name']
                    print('fdsfsdfds', profession['user_id'])
                    quit()
                except BaseException:
                    continue

    settings.save_to_json(log, original_data, settings.STEP_6_JSON_FILE)

def main():
    data = settings.load_resumes_json(log, settings.STEP_5_JSON_FILE)
    dict_with_experience_statistic = detect_experience(data)

    updated_zero_professions = change_level_for_zero_positions(dict_with_experience_statistic)

    save_update_zero_professions(updated_zero_professions, data)
    

if __name__ == "__main__":
    log = settings.start_logging("step_6.log")
    main()
