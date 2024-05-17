from __future__ import annotations

import enum
import json
import logging
import os
import zipfile
from dataclasses import asdict, dataclass
from typing import Any

from frozendict import frozendict
import requests
from bs4 import BeautifulSoup, element
from consts import DOWNLOADED_FILES_PATH, PROPERTIES_PATH
from setup import create_dirs

logger = logging.getLogger(__name__)
logger.setLevel('INFO')


class Generator:
    def __init__(self):
        self.i = 0

    def generate(self):
        self.i += 1
        return self.i - 1


id_generator = Generator().generate

HEADERS = {
    'Host': 'spbu.ru',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0',  # noqa E501
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',  # noqa E501
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br, utf-8    ',
    'Connection': 'keep-alive',
    'Cookie': '_ga=GA1.2.2008980570.1693922335; _ga_2K5KETN6FV=GS1.2.1695037316.8.1.1695037321.55.0.0; _ga_GGB4VG074D=GS1.2.1697438156.18.1.1697438316.0.0.0; _pk_ref.130.0b31=%5B%22%22%2C%22%22%2C1698221384%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_id.130.0b31=214a72a4e06148fd.1696495071.; _ga_8F1L5WCW6L=GS1.2.1698221384.5.1.1698222953.60.0.0; session-cookie=17914b599b3330162500c5d94c95548fbc85a7c30d3acb6be9373e8e4c90c89da6fc861105a2cd4c154bff2b1e36ae60; _pk_ses.130.0b31=1; _gid=GA1.2.202221708.1698221384',  # noqa E501
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'If-None-Match': 'W/"1698222845"',
}
SPBU_EDU_URL = 'https://spbu.ru/sveden/education'
DOWNLOAD_LINK = 'https://nc.spbu.ru/index.php/s/'


class Table(enum.StrEnum):
    ep_desc = 'Информация об описании образовательных программ'


@dataclass
class Link:
    column: str
    link: Any

    @classmethod
    def from_row(cls, row) -> list[Link]:
        column_names = [
            'Описание образовательной программы с приложением ее копии',
            'Учебный план',
            'Аннотации к рабочим программам дисциплин (по каждой дисциплине в составе обрзовательной программы)',  # noqa E501
            'Рабочие программы (по каждой дисциплине в составе образовательной программы)',
            'Календарный учебный график',
            'Рабочие программы практик, предусмотренных соответствующей образовательной программой',
            'Методические и иные документы, разработанные образовательной организацией для обеспечения образовательного процесса, а также рабочие программы воспитания и календарные планы воспитательной работы, включаемых в ООП',  # noqa E501
        ]

        res = []
        links_iter = (c.find_all('a') for c in row[-len(column_names) :])

        for column, links in zip(column_names[:1], links_iter):
            for link in links:
                res.append(cls(column=column, link=link))

        return res


@dataclass
class EpDescRow:
    id: int
    code: str
    field: str
    level: str
    name: str
    links: list[Link]

    @classmethod
    def from_row(cls, row) -> EpDescRow:
        links = Link.from_row(row)

        return cls(
            id=id_generator(),
            code=row[0].text,
            field=row[1].text,
            level=row[2].text,
            name=row[3].text,
            links=links,
        )

    def into_dict(self) -> frozendict:
        res = asdict(self)
        res.pop('links')
        res.pop('id')
        return frozendict(res)


def create_json_rows(rows: list[EpDescRow]):
    with open(f'{PROPERTIES_PATH}/properties.json', 'w') as fp:
        json.dump({r.id: r.into_dict() for r in rows}, fp, indent=4)


def get_info_from_ep_desc(soup: BeautifulSoup, codes: set[str]):
    target_header = soup.find('h3', string='Информация об описании образовательных программ')
    if target_header:
        create_dirs()
        assert isinstance(table := target_header.find_next('table'), element.Tag)

        print('found table, collecting rows')

        table = table.find_all('tr')

        rows: list[EpDescRow] = []

        for row in table:
            row = row.find_all('td')
            if row[0].text in codes:
                row = EpDescRow.from_row(row)
                rows.append(row)

        print('collection complete')
        print('saving properties')

        create_json_rows(rows)

        print('properties saved')
        print('downloading files')

        counter = 1
        for row in rows:
            for link in row.links:
                link = link.link
                catalog_url = link['href'].strip()
                file_name = link.text
                catalog_response = requests.get(catalog_url)
                if catalog_response.status_code == 200:
                    catalog = BeautifulSoup(catalog_response.text, 'html.parser')
                    assert isinstance(
                        download_link := catalog.select_one('.primary.button'), element.Tag
                    )
                    download_link = download_link['href']

                    print(f'downloading {file_name}')

                    if isinstance(download_link, list):
                        download_link = download_link[0]

                    print(counter, f'{catalog_url}/{file_name}.zip')
                    counter += 1
                    folder_name = catalog_url.split('/')[-1]
                    response = requests.get(DOWNLOAD_LINK + folder_name + '/download')

                    print('downloading completed')

                    if not os.path.exists(path := f'{DOWNLOADED_FILES_PATH}/{row.id}'):
                        os.makedirs(path)

                    with open(f'{DOWNLOADED_FILES_PATH}/{row.id}/{folder_name}.zip', 'wb') as file:
                        file.write(response.content)
                    with zipfile.ZipFile(
                        f'{DOWNLOADED_FILES_PATH}/{row.id}/{folder_name}.zip', 'r'
                    ) as zip_ref:
                        zip_ref.extractall(f'{DOWNLOADED_FILES_PATH}/{row.id}/{folder_name}')
                    if os.path.exists(f'{DOWNLOADED_FILES_PATH}/{row.id}/{folder_name}.zip'):
                        os.remove(f'{DOWNLOADED_FILES_PATH}/{row.id}/{folder_name}.zip')
                else:
                    print(
                        "f'Ошибка {catalog_response.status_code} при загрузке страницы с файлами'"
                    )
    else:
        print("Заголовок 'Информация об описании образовательных программ' не найден на странице.")


def get_info_from_table(table: Table, code=set()):
    d = {Table.ep_desc: get_info_from_ep_desc}

    spbu_edu_response = requests.get(SPBU_EDU_URL, headers=HEADERS)
    if spbu_edu_response.status_code == 200:
        spbu_edu = BeautifulSoup(spbu_edu_response.text, 'html.parser')
        d[table](spbu_edu, code)
    else:
        print(f'Ошибка {spbu_edu_response.status_code} при загрузке основной страницы')


table = Table.ep_desc
code = {'02.03.01'}
get_info_from_table(table, code)
