import os
from glob import glob
import shutil

import pymysql
from pymysql import Connection
from pymysql.cursors import DictCursor

from data import Match
from ocr_files import read_pdf, read_docx
from consts import HOST, PORT, PROCESSED_FILES_PATH, DOWNLOADED_FILES_PATH


# функция для подключения к серверу и создание базы данных
def create_db():
    with pymysql.connect(host=HOST, port=PORT) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                ' CREATE TABLE IF NOT EXISTS files'
                ' ('
                ' file_name string attribute indexed,'
                ' url string,'
                ' content text'
                ' )'
                " morphology='stem_enru'"
            )
        connection.commit()


def get_connection() -> Connection:
    return pymysql.connect(host=HOST, port=PORT, cursorclass=DictCursor)


def process_file(file: str, text: str, cursor: DictCursor, connection: Connection):
    file_name = file.split(os.sep)[-1]
    url = f'https://nc.spbu.ru/s/{file.split(os.sep)[-3]}/download?path=%2F&files={file_name}'
    cursor.execute(
        'INSERT INTO files (file_name, url, content) VALUES (%s, %s, %s)',
        (file_name, url, text),
    )
    connection.commit()
    shutil.move(file, PROCESSED_FILES_PATH)


# первичное добавление документов после парсинга в базу данных
def data_for_databases():
    for file in (
        set(glob(f'{DOWNLOADED_FILES_PATH}/**/*', recursive=True))
        - set(glob(f'{DOWNLOADED_FILES_PATH}/**/*.docx', recursive=True))
        - set(glob(f'{DOWNLOADED_FILES_PATH}/**/*.pdf', recursive=True))
    ):
        if not os.path.isdir(file):
            os.remove(file)
        elif not os.listdir(file):
            os.rmdir(file)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            # чтение и сохранение данных из файлов формата docx
            # (которые сохранили в папку после работы парсера)
            for file in glob(f'{DOWNLOADED_FILES_PATH}/**/*.docx', recursive=True):
                text = read_docx(file)
                process_file(file, text, cursor, connection)

            # чтение и сохранение данных из файлов формата pdf
            # (которые сохранили в папку после работы парсера)
            for file in glob(f'{DOWNLOADED_FILES_PATH}/**/*.pdf', recursive=True):
                text = read_pdf(file)
                process_file(file, text, cursor, connection)


# функция для полнотекстового поиска
def get_matches(search_str: str) -> list[Match]:
    res = []
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT file_name, url, highlight() FROM files WHERE MATCH(%s)',
                (search_str,),
            )
            result = cursor.fetchall()
            for row in result:
                res.append(
                    Match(url=row['url'], title=row['file_name'], preview=row['highlight()'])
                )
    return res
