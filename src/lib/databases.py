import json
import os
import shutil
from glob import glob

import pymysql
from consts import (
    DOWNLOADED_FILES_PATH,
    HOST,
    PORT,
    PROCESSED_FILES_PATH,
    PROPERTIES_PATH,
)
from data import Match
from ocr_files import read_docx, read_pdf
from pymysql import Connection
from pymysql.cursors import DictCursor


# функция для подключения к серверу и создание базы данных
def create_db():
    with pymysql.connect(host=HOST, port=PORT) as connection:
        with connection.cursor() as cursor:
            cursor.execute('DROP TABLE IF EXISTS files')
            connection.commit()

            cursor.execute('DROP TABLE IF EXISTS properties')
            connection.commit()

            cursor.execute(
                ' CREATE TABLE IF NOT EXISTS properties'
                ' ('
                ' id bigint,'
                ' code string attribute,'
                ' field string attribute,'
                ' level string attribute,'
                ' name string attribute'
                ' )'
            )
            connection.commit()

            cursor.execute(
                ' CREATE TABLE IF NOT EXISTS files'
                ' ('
                ' file_name string attribute indexed,'
                ' url string attribute,'
                ' content text,'
                ' properties_id bigint'
                ' )'
                " morphology='stem_enru'"
            )
            connection.commit()


def get_connection() -> Connection:
    return pymysql.connect(host=HOST, port=PORT, cursorclass=DictCursor)


def process_properties(cursor: DictCursor, connection: Connection):
    with open(f'{PROPERTIES_PATH}/properties.json') as f:
        properties: dict = json.load(f)

    for property in properties:
        cursor.execute(
            'INSERT INTO properties (id, code, field, level, name) VALUES (%s, %s, %s, %s, %s)',
            (
                property['id'],
                property['code'],
                property['field'],
                property['level'],
                property['name'],
            ),
        )

    connection.commit()


def process_file(file: str, text: str, cursor: DictCursor, connection: Connection):
    chunks = file.split(os.sep)
    index = chunks.index('downloaded')
    id = int(chunks[index + 1])
    dir = '%2F'.join(chunks[index + 4 : -1])
    url = f'https://nc.spbu.ru/index.php/s/{chunks[index+2]}/download?path=%2F{dir}&files={chunks[-1]}'
    file_name = chunks[-1]
    cursor.execute(
        'INSERT INTO files (file_name, url, content, properties_id) VALUES (%s, %s, %s, %s)',
        (file_name, url, text, id),
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
            process_properties(cursor, connection)

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
