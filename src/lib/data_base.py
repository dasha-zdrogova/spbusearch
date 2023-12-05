import pymysql
from glob import glob
from ocr_files import read_docx, ocr_pdf


try:


    #подключаемся к серверу
    with pymysql.connect(
        host = "127.0.0.1",
        user='root',
        password='12345678',
    ) as connection:
        #создаем нужную базу данных
        create_db_query = "CREATE DATABASE IF NOT EXISTS spbusearch"
        with connection.cursor() as cursor:
            cursor.execute(create_db_query)


except Exception as e:
    print(e)


try:

    #подключаемся к созданной базе данных
    with pymysql.connect(
        host = "127.0.0.1",
        user='root',
        password='12345678',
        database="spbusearch"
    ) as connection:
        

        #создаем таблицу, в которую будем сохранять инфу по файлам для индексации
        with connection.cursor() as cursor:
            create_table_query = "CREATE TABLE files (id int AUTO_INCREMENT, file_name varchar(100), URL varchar(100), content text, PRIMARY KEY(id));"
            cursor.execute(create_table_query)
            connection.commit()


        #чтение и сохранение данных из файлов формата docx (которые сохранили в папку после работы парсера)
        for file in glob('**/*.docx', recursive=True):
            text = read_docx(file)
            url = file.split(sep='\\')[1]
            file_name = file.split(sep='\\')[-1]
            inserts = (file_name, url, text)
            cursor.execute(
                'INSERT INTO files (file_name, URL, content) VALUES (%s, %s, %s)', file_name, url, text
            )
            connection.commit()


        #чтение и сохранение данных из файлов формата pdf (которые сохранили в папку после работы парсера)
        for file in glob('**/*.pdf', recursive=True):
            text = ocr_pdf(file)
            url = file.split(sep='\\')[1]
            file_name = file.split(sep='\\')[-1]
            cursor.execute(
                'INSERT INTO files (file_name, URL, content) VALUES (%s, %s, %s)', file_name, url, text
            )
            connection.commit()



except Exception as e:
    print(e)