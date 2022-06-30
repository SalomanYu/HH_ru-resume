from hh_parser import Resume

from multiprocessing import Pool
from time import sleep

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import xlrd
from settings import * 
from settings import logging


class ProfessionParser(Resume):
    def __init__(self, name_db_table: str,  profession_name:str, profession_level:int, profession_weight_in_level:int, profession_weight_in_group:int):
        
        super().__init__()
        self.profession_name = profession_name
        self.profession_weight_in_group = profession_weight_in_group
        self.profession_weight_in_level = profession_weight_in_level
        self.profession_level = profession_level

        self.address = '' # категория
        self.name_db_table = name_db_table
        self.name_database = DATABASE_NAME

    def start(self):

        self.create_table(self.name_db_table)
        self.domain = 'https://hh.ru/search/resume'
        self.search(self.domain)

    def search(self, url):
        options = Options()
        options.add_argument("--headless") # ФОНОВЫЙ РЕЖИМ
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        browser = webdriver.Chrome(options=options)
        browser.get(url)
        browser.implicitly_wait(5)


        search_input = browser.find_element(By.XPATH, "//input[@id='a11y-search-input']")
        search_input.click()
        search_input.send_keys(self.profession_name)
        search_input.send_keys(Keys.ENTER)
        browser.implicitly_wait(2)
        
        search_result_url = browser.current_url
        browser.quit()
        page = 0
        while True:
            logging.info("Page num: %d", page+1)
            if self.parser_resume_list(search_result_url + f"&page={page}"):            
                page += 1
            elif self.parser_resume_list(search_result_url + f"?page={page}"):
                page += 1
            else:
                logging.warning("Pages finished.")
                return False
            break
    
    def find_required_resumes(self, url):
        try:
            req = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(req.text, 'lxml')
            all_resumes = soup.find_all('a', class_='resume-search-item__name')
            resume_urls_list = []
            for item in all_resumes:
                if item.text.lower() == self.profession_name.lower():
                    resume_urls_list.append(f"https://hh.ru{item['href']}")
            return resume_urls_list, len(all_resumes)
            
        except (BaseException, requests.exceptions.ConnectionError) as err:
            logging.error("Internet-connection failed.")            
            logging.debug("Let`s try to connect in two minute")            
            sleep(120)

    def parser_resume_list(self, url):
        resume_urls_list, count_resumes_in_page = self.find_required_resumes(url)
        logging.info("Started four processes for parsing")
        with Pool(4) as process:
                process.map_async(  func=self.parse_resume, # Функция, которая будет вызываться с аргументом
                                    iterable=resume_urls_list, # Список аргументов, которые будут передаваться по очереди
                                    error_callback=lambda x:logging.error('Thread error --> %s', x) # Что будет, если произодет ошибка в многоптоке
                )
                process.close()
                process.join()
        
        if len(resume_urls_list) > 0 or count_resumes_in_page > 0: return True
        else: return False
            

    def get_city(self, soup):
        city = soup.find('span', attrs={"data-qa": 'resume-personal-address'})
        return city.text

    
    def collect_all_resume_info(self, soup, url):
        """
        Метод собирает все методы парсера в один массив данных
        """

        experience, work_periods = self.get_experience(soup, url)
        specializations = self.get_specialization(soup)
        univer = self.get_education_info(soup)
        training = self.get_training(soup)
        languages = self.get_languages(soup)
        self.salary = self.get_salary(soup)
        key_skills = self.get_skills(soup)
        city = self.get_city(soup)
                
        if work_periods != []:
            res = []
            for work in work_periods: # Пробегаемся по количеству мест работы 
                res.append(ResumeProfessionItem(
                    weight_in_group=self.profession_weight_in_group, level=self.profession_level, 
                    weight_in_level=self.profession_weight_in_level, name=self.profession_name, category=self.address,
                    city=city, general_experience=experience, specialization=specializations, salary=self.salary,
                    university_name=univer.name, university_direction=univer.direction, university_year=univer.year,
                    languages=languages, skills=key_skills, training_name=training.name, training_direction=training.direction,
                    training_year=training.year, branch=work.branch, subbranch=work.subbranch, experience_interval=work.interval,
                    experience_duration=work.duration, experience_post=work.post, url=url))
                
            return res 
        else: # Вариант, когда нет опыта работы
            return ResumeProfessionItem(
                    weight_in_group=self.profession_weight_in_group, level=self.profession_level, 
                    weight_in_level=self.profession_weight_in_level, name=self.profession_name, category=self.address,
                    city=city, general_experience=experience, specialization=specializations, salary=self.salary,
                    university_name=univer.name, university_direction=univer.direction, university_year=univer.year,
                    languages=languages, skills=key_skills, training_name=training.name, training_direction=training.direction,
                    training_year=training.year, branch='', subbranch='', experience_interval='',experience_duration='',
                    experience_post='', url=url)
    
    def create_table(self, name):
        cursor, db = self.connect_to_db(self.name_database)

        pattern = f"""
            CREATE TABLE IF NOT EXISTS {name}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight_in_group INT,
                level INT,
                level_in_group INT,
                name_of_profession VARCHAR(255),
                category_resume VARCHAR (50),
                city VARCHAR(50),
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
        cursor.execute(pattern)
        db.commit()
        db.close()


    def add_to_table(self, name, data,many_rows=False):
        cursor, db = self.connect_to_db(self.name_database)

        pattern = f"INSERT INTO {name}(weight_in_group, level, level_in_group, name_of_profession, category_resume, city, general_experience, specialization, salary, higher_education_university,"\
            "higher_education_direction, higher_education_year, languages, skills, advanced_training_name, advanced_training_direction," \
            f"advanced_training_year, branch, subbranch, experience_interval, experience_duration, experience_post, url) VALUES({','.join('?' for i in range(23))})"

        if many_rows: 
            cursor.executemany(pattern, data) # Результат выполнения команды в скобках VALUES превратится в VALUES(?,?,?, ?n), n = len(data)
        else:
            cursor.execute(pattern, data)
 
        db.commit()
        db.close()
        if isinstance(data, list):
            logging.info("%s - added to database.", data[0].name)
        else:
            logging.info("%s - added to database.", data.name)


if __name__ == "__main__":
    excel_data = connect_to_excel()

    for item in range(len(excel_data.names)):
        logging.debug('Searching profession called - %s', excel_data.names[item])
        profession = ProfessionParser(
                        name_db_table='Accountment',
                        profession_name=excel_data.names[item], 
                        profession_level=excel_data.levels[item],
                        profession_weight_in_group=excel_data.weights_in_group[item], 
                        profession_weight_in_level=excel_data.weights_in_level[item]
                    )
        profession.start()
