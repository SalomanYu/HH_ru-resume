from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from pymorphy2 import MorphAnalyzer 

import database
from database import University

from rich.console import Console
from rich.progress import track

console = Console()

morph = MorphAnalyzer()

option = Options()
option.headless = True
web = webdriver.Chrome(options=option)


def main():
    page_num = 0
    for _ in track(range(52), description="[yellow]Progress"):
        page_num += 1
        web.get(f'https://postupi.online/vuzi/?page_num={page_num}')
        web.implicitly_wait(5)
        sleep(1)
        
        univers =  [univer.get_attribute("href") for univer in web.find_elements(By.XPATH, "//h2[@class='list__h']//a")]
        web.implicitly_wait(2)
        for univer_url in univers:
            web.get(univer_url)
            web.implicitly_wait(3)
            fullname = web.find_element(By.XPATH, "//h1[@class='bg-nd__h']").text
            city = web.find_element(By.XPATH, "//p[@class='bg-nd__pre']").text.strip()
            shortname = web.find_element(By.XPATH, "//div[@class='card-nd-pre-wrap']//h2").text
            lemm_shortname = []
            for word in shortname.split()[1:]:
                lemm_shortname.append(morph.parse(word)[0].normal_form.upper())

            database.add(University(fullname=fullname, shortname=" ".join(lemm_shortname),city=city, url=univer_url))
            web.back()

if __name__ == "__main__":
    database.create_table()
    main()
