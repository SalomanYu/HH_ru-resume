from multiprocessing import Pool

from bs4 import  BeautifulSoup
import requests 
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from saving_data import SQL
    

class Resume:
    """
    Этот класс собирает информацию о доступных резюме с сайта hh.ru
    Здесь используется немного специфический метод поиска резюме, в виду особенностей самого сайта
        1. Каждый раз при обновлении страницы со списком всех резюме, обновляется весь список. То есть динамически меняется список
        2. hh.ru предоставляет резюме лишь по 20 резюме на страницу (всего 250 страницы) , то есть 5000 штук за один пагинатор. 
            По тз требуется собрать инфу о 1млн+ резюме
        3. В связи с ограничением количества резюме на один пагинатор, решено было использовать конструктор ссылок для парсинга.
            По следующему принципу: https://{city}.hh.ru/search/{category}
            Для этого были созданы переменные self.cities и self.parcing_urls. Ключом у self.parcing_urls является название таблицы в БД(для более удобного чтения готовых данных)  
        4. Итогая структура данных представляет собой папку SQL, в которой находятся файлы с расширением .db, отвечающие за отдельный город.
            В каждой базе данных находится len(self.parcing_urls) количество таблиц
        5. Структура любой таблицы: id(primary key желательно), group_id(ниже будет описание), название резюме, итоговый опыт работы, специализация,
            зп, Вышка(название), Вышка(направление), Вышка(год окончания), знание языков, навыки, курсы повышения квалификации(организация),
            курсы повышения квалификации(направление), курсы повышения квалификации(год окончания), отрасль, подотрасль, интервал работы в компании(инфа об опыте),
            длительность работы в компании, должность в компании, ссылка на резюме
        6. Group_id необходим по той причине, что в резюме в блоке "опыт работы" может быть указано сразу несколько мест,
            поэтому отделяем каждое место работы построчно и чтобы не перепутать резюме, мы присваем им один group_id 
    """

    def __init__(self):
        self.group_id = 0 
        self.resume_id = 0

        self.cities = ('kazan', 'spb', 'krasnodar', 'vladivostok', 'volgograd', 'voronezh', 'ekaterinburg', 'kaluga', 'krasnoyarsk', 'rostov', 'samara', 'saratov', 'sochi', 'ufa', 'yaroslavl')
        self.parcing_urls = {
            'Admin_personal': '/search/resume?professional_role=8&professional_role=33&professional_role=58&professional_role=76&professional_role=84&professional_role=88&professional_role=93&professional_role=110&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Safety': '/search/resume?professional_role=22&professional_role=90&professional_role=95&professional_role=116&professional_role=120&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Top_management': '/search/resume?professional_role=26&professional_role=36&professional_role=37&professional_role=38&professional_role=53&professional_role=80&professional_role=87&professional_role=125&professional_role=135&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Extraction_of_raw_materials': '/search/resume?professional_role=27&professional_role=28&professional_role=49&professional_role=63&professional_role=79&relocation=living_or_relocation&gender=unknown&search_period=0',
            'IT': '/search/resume?professional_role=10&professional_role=12&professional_role=25&professional_role=34&professional_role=36&professional_role=73&professional_role=96&professional_role=104&professional_role=107&professional_role=112&professional_role=113&professional_role=114&professional_role=116&professional_role=121&professional_role=124&professional_role=125&professional_role=126&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Art': '/search/resume?professional_role=12&professional_role=13&professional_role=20&professional_role=25&professional_role=34&professional_role=41&professional_role=55&professional_role=98&professional_role=103&professional_role=139&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Marketing': '/search/resume?professional_role=1&professional_role=2&professional_role=3&professional_role=10&professional_role=12&professional_role=34&professional_role=37&professional_role=55&professional_role=68&professional_role=70&professional_role=71&professional_role=99&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Medicine': '/search/resume?professional_role=8&professional_role=15&professional_role=19&professional_role=24&professional_role=29&professional_role=42&professional_role=64&professional_role=65&professional_role=133&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Science': '/search/resume?professional_role=17&professional_role=23&professional_role=79&professional_role=101&professional_role=132&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Sales': '/search/resume?professional_role=6&professional_role=10&professional_role=51&professional_role=53&professional_role=54&professional_role=57&professional_role=70&professional_role=71&professional_role=83&professional_role=97&professional_role=105&professional_role=106&professional_role=121&professional_role=122&professional_role=129&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Production': '/search/resume?professional_role=44&professional_role=45&professional_role=46&professional_role=48&professional_role=49&professional_role=63&professional_role=79&professional_role=80&professional_role=82&professional_role=85&professional_role=86&professional_role=109&professional_role=111&professional_role=115&professional_role=128&professional_role=141&professional_role=143&professional_role=144&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Consulting': '/search/resume?professional_role=10&professional_role=75&professional_role=107&professional_role=134&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Personal_management': '/search/resume?professional_role=17&professional_role=38&professional_role=69&professional_role=117&professional_role=118&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Accounting': '/search/resume?professional_role=16&professional_role=18&professional_role=50&professional_role=134&professional_role=135&professional_role=136&professional_role=137&professional_role=142&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Lawyers': '/search/resume?professional_role=145&professional_role=146&relocation=living_or_relocation&gender=unknown&search_period=0',
            'Another': '/search/resume?professional_role=40&relocation=living_or_relocation&gender=unknown&search_period=0'
        }

        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}

    def start(self):

        """
        Основная функция, которая осуществляет переход по всем городам и категориям
        """

        for self.city in self.cities: # Отбираем каждый город из списка по отдельности
            for self.address in self.parcing_urls: # Запускаем цикл по отфильтрованным по ссылкам категории
                print(f'{self.city}-{self.address}') # Принт просто для того, чтобы понимать с какой категорией сейчас работаем

                # Этот цикл отвечает за перелистывание страниц
                url = f'https://{self.city}.hh.ru' + self.parcing_urls[self.address] 
                for page_num in range(1): # 250
                    self.page_url = f"{url}&page={page_num}"
                    self.parser_resume_list()

    def parser_resume_list(self):
        
        """
        Функция, запускающая многопоточность
        """
        
        req = requests.get(self.page_url, headers=self.headers) # открываем страницу со списком резюме
        soup = BeautifulSoup(req.text, 'lxml')

        resume_urls_list = [f"https://{self.city}.hh.ru{item['href']}" for item in soup.find_all('a', class_='resume-search-item__name')] # Создаем список ссылок всех резюме        
        
        with Pool(4) as process:
            process.map_async(self.parse_resume, resume_urls_list, callback=self.data_resume_list, error_callback=lambda x:print(f'Thread error --> {x}'))
            process.close()
            process.join()
        
        quit() # Эта строчка просто для тестирования, чтобы после выполнения правильность заполнения таблицы
    
    def data_resume_list(self, response):

        """
        Функция, срабатывающая после завершения многопоточного парсинга. Она будет записывать спарсенные данные в таблицы
        """

        # Создаем sql-таблицу для каждой категории
        self.database = SQL(self.city.upper())

        for row in response:
            self.group_id += 1
            if type(row[0]) == tuple: # Условие необходимо для резюме, у которых несколько мест работы. Поэтому они возвращают список с кортежами строк для записи в БД 
                self.database.add_to_table(self.address, row, many_rows=True)
            else: # Здесь строки записываются по одному
                self.database.add_to_table(self.address, row)
            
    def parse_resume(self, url):

        """
        Функция запускает методы парсинга отдельных блоков резюме и передает результат в виде списка или списка кортежей функции data_resume_list
        """

        # Закомментированные строки используются для тестирования отдельных резюме
        # self.url = 'https://kazan.hh.ru/resume/8998d3300000c42b8d0039ed1f4466736f7571?hhtmFrom=resume_search_result'
        # self.url = 'https://kazan.hh.ru/resume/f940cf83000386bd5c0039ed1f4758516e6b64?hhtmFrom=resume_search_result'
        # req = requests.get(self.url, headers=self.headers)
        # self.soup = BeautifulSoup(req.text, 'lxml')
        # print(self.get_experience(self.soup, self.url))
        # print(self.add_row_to_table(self.soup, self.url))
        
        self.req = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(self.req.text, 'lxml')
        data = self.add_row_to_table(soup, url) # Мы передаем soup и затем переопределяем его, чтобы из-за многопоточности не было смешиваний резюме
        
        return data
        
    def get_title(self, soup):

        """
        Метод получения наименования резюме
        """

        self.soup = soup
        title = self.soup.find(attrs={'data-qa': 'resume-block-title-position', 'class': 'resume-block__title-text'}).text
        
        return title

    def get_salary(self, soup):

        """
        Метод получения зарплаты резюме
        """

        self.soup = soup
        salary = self.soup.find('span', class_='resume-block__salary resume-block__title-text_salary')

        if salary:
            return salary.text
        else: 
            return ''
    
    def get_education_info(self, soup):

        """
        Метод получения информации об образовании
        """

        self.soup = soup
        # education_direction = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find('div', attrs={'data-qa': 'resume-block-education-organization'})
        specializations =  [item.text for item in self.soup.find_all('li', class_='resume-block__specialization')] # Забираем перечень специализаций
        # переменная нужна, чтобы понять указано ли учебное заведение в описании образования или нет
        education_type = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find(class_='bloko-header-2').text 
        
        # список всех учебных заведений
        educations_list = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find('div', class_='resume-block-item-gap').find_all('div', class_='resume-block-item-gap')
        if len(educations_list) > 0: 
            education_names_list = []
            education_directions_list = []
            education_years_list = []
            for item in educations_list:
                name = item.find(attrs={'data-qa':'resume-block-education-name'}).text 
                # Тут прописывается проверка указано ли направление образования или нет. Обычно направления нет у тех, кто оканчивал только школу
                direction = '' if item.find(attrs={'data-qa':'resume-block-education-organization'}) == None else item.find(attrs={'data-qa':'resume-block-education-organization'}).text
                year = item.find('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2').text
                
                education_names_list.append(name)
                education_directions_list.append(direction)
                education_years_list.append(year)
            return ' | '.join(specializations), ' | '.join(education_names_list), ' | '.join(education_directions_list), ' | '.join(education_years_list)
        
        else: # Если в разделе Образование написано просто - среднее образование
            if education_type == 'Образование':
                education_type = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find_all('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-8 bloko-column_m-9 bloko-column_l-12')[-1].text
                return ' | '.join(specializations), education_type, '', '' 


    def get_skills(self, soup):

        """
        Метод получения информации о навыках
        """

        self.soup = soup
        try:
            if self.soup.find('div', class_='bloko-tag-list') != None: # Проверяем существует ли блок с навыками соискателя
                skills_html = self.soup.find('div', class_='bloko-tag-list').find_all('span')
                key_skills = []
                for item in skills_html:
                    key_skills.append(item.text)
                return ' | '.join(key_skills) if type(key_skills) == list else key_skills

            else:
                return ''
        except AttributeError:
            return ''

    def get_languages(self, soup):
        
        """
        Метод получения информации о доступных языках
        """

        self.soup = soup
        languages = [item.text for item in self.soup.find(attrs={'data-qa': 'resume-block-languages'}).find_all('p')]
        edited_languages = []
        for language in languages:
            new_lang = language.split('—')[0] + f"({language.split(' — ')[1]})" # Приводим к виду [ Русский ( Родной); Английский ( B2 — Средне-продвинутый) ]
            edited_languages.append(new_lang)

        return " | ".join(edited_languages)
    
    def get_experience(self, soup, url):
        """
        Метод получения информации об опыте работы
        """
        
        self.soup = soup
        # Что означают эти переменные странные?
        # work_spaces - ....
        # Надо написать подробное описание метода
        work_soup = self.soup # Потребуется для изменения soup внутри функции во время вызова selenium

        work_spaces = work_soup.find(attrs={'data-qa': 'resume-block-experience', 'class': 'resume-block'})
        self.work_periods = []
        if work_spaces == None:
            self.total_work_experience = ''
            self.work_periods.append({
                'Должность': '',
                'Промежуток': '',
                'Отрасль':'',
                'Подотрасль': '',
                'Продолжительность': ''
            })
        else:
            if work_soup.find('span', class_='resume-industries__open'):
                options = Options()
                options.add_argument("--headless") # ФОНОВЫЙ РЕЖИМ
                
                browser = webdriver.Chrome(options=options)
                browser.get(url)
                # browser.get(self.url)
                browser.implicitly_wait(3)

                see_more_btns = browser.find_elements(By.XPATH, "//span[@class='resume-industries__open']")
                for btn in see_more_btns: btn.click()     
                work_soup = BeautifulSoup(browser.page_source, 'lxml') # Переопределение soup`a 
                work_spaces = work_soup.find(attrs={'data-qa': 'resume-block-experience', 'class': 'resume-block'}) # Переопределение опыта                
                browser.quit()


            self.total_work_experience = work_soup.find('span', class_='resume-block__title-text resume-block__title-text_sub').text
            if 'опыт работы' in self.total_work_experience.lower():
                self.total_work_experience = self.total_work_experience.replace(u'\xa0', u' ').replace('Опыт работы', '')
            else:
                self.total_work_experience = work_soup.find_all('span', class_='resume-block__title-text resume-block__title-text_sub')[1].text.replace(u'\xa0', u' ').replace('Опыт работы', '')

            
            for work in work_spaces.find_all('div', class_='resume-block-item-gap')[1:]:
                period = work.find('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2').text.replace(u'\xa0', u' ')
                period_new = re.split('\d \w', period)[0]
                months_count = period[re.search('\d \w', period).start():]
                work_title = work.find('div', {'data-qa':'resume-block-experience-position',"class":'bloko-text bloko-text_strong'}).text
                try:
                    branch = [item.text for item in work.find('div', class_='resume-block__experience-industries resume-block_no-print').find_all('p')]
                    subranches = []
                    # Следующий цикл для подотраслей такого типа: https://kazan.hh.ru/resume/8bbd526100027d2f200039ed1f323563626552?hhtmFrom=resume_search_result
                    for item in work.find('div', class_='resume-block__experience-industries resume-block_no-print').find_all('ul'):
                        subranches.append(' ; '.join([li.text for li in item.find_all('li')]))
                except BaseException:
                    branch = [work.find('div', class_='resume-block__experience-industries resume-block_no-print').text.split('...')[0]]
                    subranches = []

                self.work_periods.append({
                    'Должность': work_title,
                    'Отрасль': ' | '.join(branch),
                    'Подотрасль': ' | '.join(subranches),
                    'Промежуток': period_new,
                    'Продолжительность': months_count
                })
        return self.work_periods, self.total_work_experience
    
    def get_training(self, soup):
        
        """
        Метод получения информации о повышении квалификации
        """

        self.soup = soup
        try:
            training_html = self.soup.find('div', attrs={'data-qa': 'resume-block-additional-education', 'class':'resume-block'}).find('div', class_='resume-block-item-gap').find_all('div', 'resume-block-item-gap')
            if len(training_html) > 0:
                education_names_list = []
                education_directions_list = []
                education_years_list = []
                for item in training_html:
                    year = item.find('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2').text
                    company = item.find(attrs={'data-qa':'resume-block-education-name'}).text
                    direction = item.find(attrs={'data-qa':'resume-block-education-organization'}).text
                    
                    education_names_list.append(company)
                    education_directions_list.append(direction)
                    education_years_list.append(year)
                return ' | '.join(education_names_list), ' | '.join(education_directions_list), ' | '.join(education_years_list)
            else:
                return '', '', ''
        except BaseException:
            return '', '', ''
        
            
    def add_row_to_table(self, soup, url):
        """
        Метод собирает все методы парсера в один массив данных
        """

        work_periods, experience = self.get_experience(soup, url)
        specializations,  education_name, education_direction, education_year = self.get_education_info(soup)
        training_name, training_direction, training_year = self.get_training(soup) 
        languages = self.get_languages(soup)
        self.salary = self.get_salary(soup)
        key_skills = self.get_skills(soup)
        title = self.get_title(soup)
        
        print(title)    
                
        if len(work_periods) > 1:
            res = []
            for item in work_periods: # Пробегаемся по количеству мест работы 
                self.resume_id += 1
                data = (
                        self.resume_id,
                        self.group_id,
                        title,
                        experience,
                        specializations,
                        self.salary,
                        education_name, 
                        education_direction,
                        education_year,
                        languages,
                        key_skills,
                        training_name,
                        training_direction,
                        training_year,
                        item['Отрасль'],
                        item['Подотрасль'],
                        item['Промежуток'],
                        item['Продолжительность'],
                        item['Должность'],
                        url
                )
                
                res.append(data)
            return res 
        else: # Вариант, когда нет опыта работы
            self.resume_id += 1
            data = (
                    self.resume_id,
                    self.group_id,
                    title,
                    experience,
                    specializations,
                    self.salary,
                    education_name, 
                    education_direction,
                    education_year,
                    languages,
                    key_skills,
                    training_name,
                    training_direction,
                    training_year,
                    '',
                    '',
                    '',
                    '',
                    '',
                    url
            )
            return data


bot = Resume()
bot.start()
