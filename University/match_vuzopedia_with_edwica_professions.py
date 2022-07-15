import xlrd
import os

from rich.progress import track

PROFESSION_FOLDER = "Professions"
VUZOPEDIA_FILE = "/home/yunoshev/Documents/Edwica/Other/20.Vuzopedia/Vuzopedia.xlsx"

def get_edwica_professions() -> frozenset:
    EDWICA_PROFESSIONS = []
    for prof_file in os.listdir(PROFESSION_FOLDER):
        work_file = os.path.join(PROFESSION_FOLDER, prof_file)
        wb = xlrd.open_workbook(work_file)
        sheet = wb.sheet_by_name("Список профессий")
    
        table_titles = sheet.row_values(0)
        for title_col in range(len(table_titles)):
            if table_titles[title_col] == "Название 1-го уровня":
                column = title_col
        
        for profession in sheet.col_values(column)[1:]:
            EDWICA_PROFESSIONS.append(profession)
    return frozenset(EDWICA_PROFESSIONS)


def get_vuzopedia_professions() -> frozenset:
    VUZOPEDIA_PROFESSIONS = []
    wb = xlrd.open_workbook(VUZOPEDIA_FILE)
    sheet = wb.sheet_by_name("Профессии")
    
    table_titles = sheet.row_values(0)
    for title_col in range(len(table_titles)):
        if table_titles[title_col] == "Название профессии":
            column = title_col
    for profession in sheet.col_values(column)[1:]:
        VUZOPEDIA_PROFESSIONS.append(profession)
    return frozenset(VUZOPEDIA_PROFESSIONS)



if __name__ == "__main__":
    ed_prof = get_edwica_professions()
    vuz_prof = get_vuzopedia_professions()
    
    match_count = len(ed_prof & vuz_prof)
    # mismatch_count = len(ed_prof) - match_count 
    
    match_professions = set()
    mismatch_professions = set()

    for prof in vuz_prof:
        if prof in ed_prof:
            match_professions.add(prof)
        else:
            mismatch_professions.add(prof)
    
    match_file = open("match_professions_ed.txt", "w")
    match_file.write(f"Количество совпадений: {match_count}\n\n")
    match_file.write("\n".join(match_professions))
    match_file.close()

    mismatch_file = open("mismatch_professions_ed.txt", "w")
    mismatch_file.write(f"Этих профессий нет в базе Эдвики': {len(mismatch_professions)}\n\n")
    mismatch_file.write("\n".join(mismatch_professions))
    mismatch_file.close()