import xlrd
import os

# from google.oauth2 import service_account
# from googleapiclient.http import MediaIoBaseDownload, MediaInMemoryUpload
# from googleapiclient.discovery import build


# from oauth2client.service_account import ServiceAccountCredentials
# import gspread

from bs4 import BeautifulSoup
import requests
import sqlite3


def connect_to_google():
    scopes = ['https://www.googleapis.com/auth/drive']
    service_account_file = '/home/yunoshev/Documents/credentials.json'
    credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
    service = build('drive', 'v3', credentials=credentials)
    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
    print(results)
    # gc = gspread.authorize(credentials)
    # spread = gc.open_by_key('1gie16-NwALi22hdNiZmv4IdnDW5vmW4nqljbeRgmku4')

# print(connect_to_google())


def add_date_toSQL():

    db = sqlite3.connect("TESTDB.db")
    cursor = db.cursor()
    # cursor.execute(
    #     """CREATE TABLE testing (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name VARCHAR(250),
    #         my_date DATE DEFAULT CURRENT_TIMESTAMP
    #     )"""
    # )
    cursor.execute("INSERT INTO testing(name) VALUES(? )", "yarik")
    db.commit()
    db.close()


add_date_toSQL()