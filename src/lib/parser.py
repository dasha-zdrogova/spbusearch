import enum
import requests
from bs4 import BeautifulSoup, element
import os
import zipfile

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


class Table(enum.StrEnum):
    ep_desc = 'Информация об описании образовательных программ'


def get_info_from_ep_desc(soup: BeautifulSoup, code):
    target_header = soup.find('h3', string='Информация об описании образовательных программ')
    if target_header:
        if not os.path.exists('files'):
            os.makedirs('files')
        assert isinstance(table := target_header.find_next('table'), element.Tag)
        table = table.find_all('tr')

        links = []

        for row in table:
            info = row.find_all('td')
            if code:
                if info[0].text in code:
                    print(info[0].text, code)
                    links.append(info[6].find_all('a'))

        counter = 1
        for i in range(len(links)):
            for link in links[i]:
                catalog_url = link['href'].strip()
                file_name = link.text
                catalog_response = requests.get(catalog_url)
                if catalog_response.status_code == 200:
                    catalog = BeautifulSoup(catalog_response.text, 'html.parser')
                    assert isinstance(
                        download_link := catalog.select_one('.primary.button'), element.Tag
                    )
                    download_link = download_link['href']
                    if isinstance(download_link, list):
                        download_link = download_link[0]

                    print(counter, f'./files/{catalog_url}/{file_name}.zip')
                    counter += 1
                    folder_name = catalog_url.split('/')[-1]
                    response = requests.get(download_link)

                    with open(f'./files/{folder_name}.zip', 'wb') as file:
                        file.write(response.content)
                    with zipfile.ZipFile(f'./files/{folder_name}.zip', 'r') as zip_ref:
                        zip_ref.extractall(f'./files/{folder_name}')
                    if os.path.exists(f'./files/{folder_name}.zip'):
                        os.remove(f'./files/{folder_name}.zip')
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


table_instance = Table.ep_desc
code = {'02.03.01'}
get_info_from_table(table_instance, code)
