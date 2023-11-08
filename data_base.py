import psycopg2
import os
from glob import glob
from ocr_files import read_docx, ocr_pdf

#подключаемся к базе данных
try:
    conn = psycopg2.connect(dbname='spbu_search', user='postgres', password='1234567', host="localhost", port="5432")
    print("Connection to PostgreSQL DB successful")
except:
    print('Cant establish connection to database')

conn.autocommit = True

cur = conn.cursor()

#создаем внутри базы данных таблицу с содержимым файлов
cur.execute('''CREATE TABLE files  
    (id serial PRIMARY KEY,
     file_name varchar(100) NOT NULL,
     URL varchar(100) NOT NULL,
     content text);''')

#для каждого файла указанного расширения извлекаем имя файла, url из названия папки и текст документа
for file in glob('**/*.docx', recursive=True):
    text = read_docx(file)
    url = file.split(sep="\\")[1]
    file_name = file.split(sep="\\")[-1]
    inserts = (file_name, url, text)
    cur.execute("INSERT INTO files (file_name, URL, content) VALUES (%s, %s, %s)", file_name, url, text)

for file in glob('**/*.pdf', recursive=True):
    text = ocr_pdf(file)
    url = file.split(sep="\\")[1]
    file_name = file.split(sep="\\")[-1]
    cur.execute("INSERT INTO files (file_name, URL, content) VALUES (%s, %s, %s)", file_name, url, text)

cur.close()
conn.close()