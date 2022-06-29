from step_3_remove_repeat_groupes import load_resumes_json

def detect_similar_trajectories(data):
    resumes = list(data.items())

    for current_index in range(len(resumes)):
        current_name = resumes[current_index][1][0]['name_of_profession']
        current_steps_len = len(resumes[current_index][1])
        current_steps = resumes[current_index][1]

        for comporable_index in range(current_index+1, len(resumes)):
            comporable_name = resumes[comporable_index][1][0]['name_of_profession']
            comporable_steps_len = len(resumes[comporable_index][1])
            comporable_steps = resumes[comporable_index][1]

            # if (current_steps_len == comporable_steps_len): # Вариант без учета названия
            if (current_name == comporable_name) and (current_steps_len == comporable_steps_len):
                similar_steps_count = 0
                for step in range(current_steps_len):
                    current_step = current_steps[step]['experience_post']
                    comporable_step = comporable_steps[step]['experience_post']
                    if current_step == comporable_step:
                        similar_steps_count += 1
                if similar_steps_count == current_steps_len:
                    print(resumes[current_index][0])
                    print(resumes[comporable_index][0])
                    print('---------')

if __name__ == "__main__":
    data = load_resumes_json('JSON/step_6_update_zero_levels.json')
    detect_similar_trajectories(data)