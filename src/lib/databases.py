from glob import glob
import shutil

import pymysql
from pymysql import Connection
from pymysql.cursors import DictCursor

from data import Match
from ocr_files import ocr_pdf, read_docx
from consts import HOST, PORT, NEW_FILES_PATH, PROCESSED_FILES_PATH


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
    url = file.split(sep='\\')[1]
    file_name = file.split(sep='\\')[-1]
    cursor.execute(
        'INSERT INTO files (file_name, url, content) VALUES (%s, %s, %s)',
        (file_name, url, text),
    )
    connection.commit()
    shutil.move(file, PROCESSED_FILES_PATH)


# первичное добавление документов после парсинга в базу данных
def data_for_databases():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            # чтение и сохранение данных из файлов формата docx
            # (которые сохранили в папку после работы парсера)
            for file in glob(f'{NEW_FILES_PATH}/*.docx', recursive=True):
                text = read_docx(file)
                process_file(file, text, cursor, connection)

            # чтение и сохранение данных из файлов формата pdf
            # (которые сохранили в папку после работы парсера)
            for file in glob(f'{NEW_FILES_PATH}/*.pdf', recursive=True):
                text = ocr_pdf(file)
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
