import sqlite3
import os


class SQL:
    def __init__(self, db_name):
        self.db_name = db_name
        os.makedirs('SQL', exist_ok=True) # Создаем папку SQL, если она еще не создана

        self.db = sqlite3.connect(f'SQL/{db_name}.db')
        self.cursor = self.db.cursor()

    def create_table(self, name):
        pattern = f"""
            CREATE TABLE IF NOT EXISTS {name}(
                id INT,
                group_id INT,
                name_of_profession VARCHAR(255),
                general_experience VARCHAR(50),
                specialization VARCHAR(255),
                salary VARCHAR(50),
                higher_education_university TEXT,
                higher_education_direction TEXT,
                higher_education_year VARCHAR(100),
                languages VARCHAR(255),
                skills TEXT,
                advanced_training_name TEXT,
                advanced_training_direction TEXT,
                advanced_training_year VARCHAR(100),
                branch VARCHAR(255),
                subbranch VARCHAR(255),
                experience_interval VARCHAR(50),
                experience_duration VARCHAR(50),
                experience_post VARCHAR(255),
                url VARCHAR(255)
                );
            """
        self.cursor.execute(pattern)
        self.db.commit()

    def add_to_table(self, name, data,many_rows=False):
        # self.group_id = group_id
        self.create_table(name)
        pattern = f"INSERT INTO {name} VALUES({','.join('?' for i in range(20))})"

        if many_rows:
            # Результат выполнения команды в скобках VALUES превратится в VALUES(?,?,?, ?n), n = len(data) 
            self.cursor.executemany(pattern, data)
        else:
            # pattern = f"INSERT INTO {name} VALUES({','.join('?' for i in range(20))})"
            self.cursor.execute(pattern, data)
 
        self.db.commit()

if __name__ == "__main__":
    # For testing writing
    t = SQL('test')
    # data = (1, 1, 'Персональный  водитель. Помощник. Стаж 21 год. Имею оружие.', 'Анкета водителя', <__main__.Resume object at 0x7f0adcde4610>, 'Секретарь, помощник руководителя, ассистент | Охранник | Водитель', '', 'Кемеровский государственный сельскохозяйственный институт, Кемерово', 'Факультет аграрных технологий, Автоматизация технологических процессов и производств (по отраслям)', '1997', 'Русский (Родной)', 'Опыт работы на автомобилях различного класса 20 лет, | Стаж безаварийного вождения 20 лет | Навыки экстремального вождения | Умение осознавать требования руководителя и соответствовать им | Имею опыт поездок на дальние расстояния | Есть необходимые знания и навыки для ремонта автомобиля | Навыки стрельбы', 'Свидетельство о прохождении обучения безопасному обращению с оружием | Экстремальное вождение автомобиля', 'ММУСТЦ ДОСААФ РОССИИ | Инструктор (частное лицо)', '2021 | 2021', '', '', '', '', '', 'https://kazan.hh.ru/resume/f940cf83000386bd5c0039ed1f4758516e6b64?hhtmFrom=resume_search_result')
    data = [(1, 1, 'Оператор ПК', ' 20 лет', 'Оператор ПК, оператор базы данных', '45\u2009000\xa0руб.', 'Тверской государственный университет ‚ факультет биологии) (высшее (специалист)) Тверь | Московский областной институт физической культуры ‚ (тренерский факультет) (высшее (специалист)) Москва', 'преподаватель, преподаватель | тренер-преподаватель, тренер-преподаватель', '1991 | 1989', 'Русский (Родной) | Английский (A1)', '', '1С Бухгалтерия для предпринимателя', 'Московская академия предпринимательства , Диплом от 03 декабря 2010 г.', '2010', '', '', 'Декабрь 2012 — по настоящее время', '9 лет 5 месяцев', 'Директор, продавец', 'https://kazan.hh.ru/resume/8998d3300000c42b8d0039ed1f4466736f7571?hhtmFrom=resume_search_result'), (2, 1, 'Оператор ПК', ' 20 лет', 'Оператор ПК, оператор базы данных', '45\u2009000\xa0руб.', 'Тверской государственный университет ‚ факультет биологии) (высшее (специалист)) Тверь | Московский областной институт физической культуры ‚ (тренерский факультет) (высшее (специалист)) Москва', 'преподаватель, преподаватель | тренер-преподаватель, тренер-преподаватель', '1991 | 1989', 'Русский (Родной) | Английский (A1)', '', '1С Бухгалтерия для предпринимателя', 'Московская академия предпринимательства , Диплом от 03 декабря 2010 г.', '2010', '', '', 'Август 2000 — Февраль 20111', '0 лет 7 месяцев', 'менеджер по продажам', 'https://kazan.hh.ru/resume/8998d3300000c42b8d0039ed1f4466736f7571?hhtmFrom=resume_search_result')]
    t.add_to_table('test', data, many_rows=False)