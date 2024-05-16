import json
import os
import shutil
from glob import glob
from typing import Any, Optional

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

            cursor.execute(
                ' CREATE TABLE IF NOT EXISTS files'
                ' ('
                ' file_name string attribute indexed,'
                ' url string attribute,'
                ' content text,'
                ' code string attribute indexed,'
                ' field string attribute indexed,'
                ' level string attribute indexed,'
                ' name string attribute indexed'
                ' )'
                " morphology='stem_enru'"
            )
            connection.commit()


def get_connection() -> Connection:
    return pymysql.connect(host=HOST, port=PORT, cursorclass=DictCursor)


def process_properties() -> dict:
    with open(f'{PROPERTIES_PATH}/properties.json') as f:
        return json.load(f)


def process_file(
    file: str, content: str, properties: dict[str, Any], cursor: DictCursor, connection: Connection
):
    chunks = file.split(os.sep)
    index = chunks.index('downloaded')
    id = chunks[index + 1]
    file_props: dict = properties[id]
    dir = '%2F'.join(chunks[index + 4 : -1])
    url = f'https://nc.spbu.ru/index.php/s/{chunks[index+2]}/download?path=%2F{dir}&files={chunks[-1]}'  # noqa E501
    file_name = chunks[-1]
    cursor.execute(
        ' INSERT INTO files (file_name, url, content, code, field, level, name)'
        ' VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (
            file_name,
            url,
            content,
            file_props['code'],
            file_props['field'],
            file_props['level'],
            file_props['name'],
        ),
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

    properties = process_properties()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            # чтение и сохранение данных из файлов формата docx
            # (которые сохранили в папку после работы парсера)
            for file in glob(f'{DOWNLOADED_FILES_PATH}/**/*.docx', recursive=True):
                text = read_docx(file)
                process_file(file, text, properties, cursor, connection)

            # чтение и сохранение данных из файлов формата pdf
            # (которые сохранили в папку после работы парсера)
            for file in glob(f'{DOWNLOADED_FILES_PATH}/**/*.pdf', recursive=True):
                text = read_pdf(file)
                process_file(file, text, properties, cursor, connection)


# функция для полнотекстового поиска
def get_matches(
    content: str,
    code: Optional[str] = None,
    field: Optional[str] = None,
    level: Optional[str] = None,
    name: Optional[str] = None,
) -> list[Match]:
    def add_to_filters(name: str, value):
        if value is not None:
            match_filters.append(f'@{name} {value}')

    match_filters = []

    add_to_filters('content', content)
    add_to_filters('code', code)
    add_to_filters('field', field)
    add_to_filters('level', level)
    add_to_filters('name', name)

    inside_match = ' '.join(match_filters)

    res = []
    with get_connection() as connection:
        with connection.cursor() as cursor:
            print(
                'fetching:\n\t'
                f'SELECT file_name, url, highlight() FROM files WHERE MATCH({inside_match})'
            )

            cursor.execute(
                'SELECT file_name, url, highlight() FROM files WHERE MATCH(%s)',
                (inside_match,),
            )

            fetch_result = cursor.fetchall()
            print(f'got {len(fetch_result)} rows from db')
            for row in fetch_result:
                res.append(
                    Match(url=row['url'], title=row['file_name'], preview=row['highlight()'])
                )
    return res
