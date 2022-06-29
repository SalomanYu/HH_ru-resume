from typing import NamedTuple
from dataclasses import dataclass
import sqlite3
import logging
import xlrd


logging.basicConfig(filename='LOGGING/step_1.log', encoding='utf-8', level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING) # Без этого urllib3 выводит страшные большие белые сообщения
logging.getLogger('selenium').setLevel(logging.WARNING)


SUCCESS_MESSAGE = '\033[2;30;42m [SUCCESS] \033[0;0m' 
WARNING_MESSAGE = '\033[2;30;43m [WARNING] \033[0;0m'
ERROR_MESSAGE = '\033[2;30;41m [ ERROR ] \033[0;0m'
EXCEL_PATH = "Excel/11 Офисные службы.xlsx"

class ExcelData(NamedTuple):
    names: tuple
    weights_in_level: tuple
    weights_in_group: tuple
    levels: tuple


def connect_to_excel() -> ExcelData:
    last_row_num = 49
    book_reader = xlrd.open_workbook(EXCEL_PATH)
    work_sheet = book_reader.sheet_by_name('Вариации названий')
    table_titles = work_sheet.row_values(0)
    for col_num in range(len(table_titles)):
        match table_titles[col_num]:
            case 'Наименование професии и различные написания':
                table_names = work_sheet.col_values(col_num)[1:last_row_num]
            case 'Вес профессии в уровне':
                table_weight_in_level = work_sheet.col_values(col_num)[1:last_row_num] # 25 Включительно
            case 'Уровень должности':
                table_level = work_sheet.col_values(col_num)[1:last_row_num]
            case 'Вес профессии в соответсвии':
                table_weight_in_group = work_sheet.col_values(col_num)[1:last_row_num]
    return ExcelData(table_names, table_weight_in_level, table_weight_in_group, table_level)


class ResumeProfessionItem(NamedTuple):
    weight_in_group: int
    level: int
    weight_in_level: int
    name: str
    category: str
    city: str
    general_experience: str
    specialization: str
    salary: str
    university_name: str
    university_direction: str
    university_year: str | int
    languages: str
    skills: str
    training_name: str
    training_direction: str
    training_year: str
    branch: str
    subbranch: str
    experience_interval: str
    experience_duration: str
    experience_post: str
    url: str

class ResumeItem(NamedTuple):
    name: str
    category: str
    city: str
    general_experience: str
    specialization: str
    salary: str
    university_name: str
    university_direction: str
    university_year: str | int
    languages: str
    skills: str
    training_name: str
    training_direction: str
    training_year: str
    branch: str
    subbranch: str
    experience_interval: str
    experience_duration: str
    experience_post: str
    url: str


class Training(NamedTuple):
    name: str
    direction: str
    year: int


class University(NamedTuple):
    name: str
    direction: str
    year: int


class WorkExperience(NamedTuple):
    post: str # Product manager
    interval: str # Март 2017 — по настоящее время
    branch: str # Информационные технологии, системная интеграция, интернет
    subbranch: str # Разработка программного обеспечения
    duration: str # 5  лет 4 месяца


class Experience(NamedTuple):
    global_experience: str # Например: 8 лет и 5 месяцев
    work_places: set[WorkExperience]


@dataclass(frozen=True, slots=True)
class RequiredUrls:
    category: str
    url: str


class Variables(NamedTuple):
    name_db: str
    cities: set['str']
    parsing_urls: set[RequiredUrls]
    headers: dict


class Connection(NamedTuple):
    cursor: sqlite3.Cursor
    db: sqlite3.Connection

HH_VARIABLES = Variables(
    name_db='HH_RU',
    cities={
        'kazan', 'spb', 'krasnodar', 'vladivostok', 'volgograd', 'voronezh', 'ekaterinburg', 'kaluga',
        'krasnoyarsk', 'rostov', 'samara', 'saratov', 'sochi', 'ufa', 'yaroslavl'
    },
    parsing_urls=(
        RequiredUrls(category='Admin_personal', url='/search/resume?professional_role=8&professional_role=33&professional_role=58&professional_role=76&professional_role=84&professional_role=88&professional_role=93&professional_role=110&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Safety', url='/search/resume?professional_role=22&professional_role=90&professional_role=95&professional_role=116&professional_role=120&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Top_management', url='/search/resume?professional_role=26&professional_role=36&professional_role=37&professional_role=38&professional_role=53&professional_role=80&professional_role=87&professional_role=125&professional_role=135&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Extraction_of_raw_materials', url='/search/resume?professional_role=27&professional_role=28&professional_role=49&professional_role=63&professional_role=79&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='IT', url='/search/resume?professional_role=10&professional_role=12&professional_role=25&professional_role=34&professional_role=36&professional_role=73&professional_role=96&professional_role=104&professional_role=107&professional_role=112&professional_role=113&professional_role=114&professional_role=116&professional_role=121&professional_role=124&professional_role=125&professional_role=126&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Art', url='/search/resume?professional_role=12&professional_role=13&professional_role=20&professional_role=25&professional_role=34&professional_role=41&professional_role=55&professional_role=98&professional_role=103&professional_role=139&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Marketing', url='/search/resume?professional_role=1&professional_role=2&professional_role=3&professional_role=10&professional_role=12&professional_role=34&professional_role=37&professional_role=55&professional_role=68&professional_role=70&professional_role=71&professional_role=99&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Medicine', url='/search/resume?professional_role=8&professional_role=15&professional_role=19&professional_role=24&professional_role=29&professional_role=42&professional_role=64&professional_role=65&professional_role=133&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Science', url='/search/resume?professional_role=17&professional_role=23&professional_role=79&professional_role=101&professional_role=132&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Sales', url='/search/resume?professional_role=6&professional_role=10&professional_role=51&professional_role=53&professional_role=54&professional_role=57&professional_role=70&professional_role=71&professional_role=83&professional_role=97&professional_role=105&professional_role=106&professional_role=121&professional_role=122&professional_role=129&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Production', url='/search/resume?professional_role=44&professional_role=45&professional_role=46&professional_role=48&professional_role=49&professional_role=63&professional_role=79&professional_role=80&professional_role=82&professional_role=85&professional_role=86&professional_role=109&professional_role=111&professional_role=115&professional_role=128&professional_role=141&professional_role=143&professional_role=144&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Consulting', url='/search/resume?professional_role=10&professional_role=75&professional_role=107&professional_role=134&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Personal_management', url='/search/resume?professional_role=17&professional_role=38&professional_role=69&professional_role=117&professional_role=118&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Accounting', url='/search/resume?professional_role=16&professional_role=18&professional_role=50&professional_role=134&professional_role=135&professional_role=136&professional_role=137&professional_role=142&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Lawyers', url='/search/resume?professional_role=145&professional_role=146&relocation=living_or_relocation&gender=unknown&search_period=0'),
        RequiredUrls(category='Another', url='/search/resume?professional_role=40&relocation=living_or_relocation&gender=unknown&search_period=0')
    ),
    headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'}
    )
