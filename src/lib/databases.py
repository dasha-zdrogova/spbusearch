import pymysql
from glob import glob
from ocr_files import read_docx, ocr_pdf


#функция для подключения к серверу и создание базы данных
def connection():
    connection = pymysql.connect(
        host =  "0",
        port = 9306)

    create_db_query = "CREATE DATABASE IF NOT EXISTS spbusearch"
    cursor = connection.cursor()
    cursor.execute(create_db_query)
    connection.commit()


# первичное добавление документов после парсинга в базу данных
def data_for_databases():
    connection = pymysql.connect(
        host = "0",
        port = 9306,
        database="spbusearch"
    )

    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE files  
        (file_name string indexed,
        URL string,
        content text) 
        morphology='lemmatize_ru_all, lemmatize_en_all, stem_enru';''')
    connection.commit()

        #чтение и сохранение данных из файлов формата docx (которые сохранили в папку после работы парсера)
    for file in glob('**/*.docx', recursive=True):
        text = read_docx(file)
        url = file.split(sep='\\')[1]
        file_name = file.split(sep='\\')[-1]
        cursor.execute("INSERT INTO files (file_name, URL, content) VALUES (%s, %s, %s)", (file_name, url, text))
        connection.commit()


    #чтение и сохранение данных из файлов формата pdf (которые сохранили в папку после работы парсера)
    for file in glob('**/*.pdf', recursive=True):
        text = ocr_pdf(file)
        url = file.split(sep='\\')[1]
        file_name = file.split(sep='\\')[-1]
        cursor.execute('INSERT INTO files (file_name, URL, content) VALUES (%s, %s, %s)', (file_name, url, text))
        connection.commit()

    cursor.execute("SELECT file_name from files")
    result = cursor.fetchall()
    for row in result:
        print(row + "добавлен в базу данных")

# функция для полнотекстового поиска
def get_matches(connection, search_str):
    cursor = connection.cursor()
    cursor.execute(f'SELECT *, HIGHLIGHT({{limit={50 + len(search_str)}}}) FROM files WHERE MATCH({search_str})')
    result = cursor.fetchall()
    for row in result:
        print(row)