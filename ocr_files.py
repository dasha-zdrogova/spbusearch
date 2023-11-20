import os
import platform
import pytesseract
import docx
from tempfile import TemporaryDirectory
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image


def ocr_pdf(file):
    if platform.system() == "Windows":
        pytesseract.pytesseract.tesseract_cmd = (r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        path_to_poppler_exe = Path(r"C:\poppler-23.11.0\Library\bin")   


    PDF_file = Path(file) #какой файл 
    #file_name = PDF_file.name

    image_file_list = []
    #text_file = out_directory / Path(file_name)
    with TemporaryDirectory() as tempdir:
        #временный каталог для хранения изображений страниц файла
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Часть 1: конвертируем pdf в картинки
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        if platform.system() == "Windows":
            pdf_pages = convert_from_path(PDF_file, 500, poppler_path=path_to_poppler_exe)
        else:
            #читаем PDF-файл с разрешением 500 точек на дюйм
            pdf_pages = convert_from_path(PDF_file, 500)

        #итерируемся по страницам, сохраненным выше
        for page_enumeration, page in enumerate(pdf_pages, start=1):
            #создаем имя файла для сохранения изображения
            filename = f"{tempdir}\page_{page_enumeration:03}.jpg"
    
            #объявляем имя файла для каждой страницы PDF в формате jpg
            #для каждой страницы имя файла будет таким: pdf page 1 -> page_001.jpg

            #сохраняем картинки
            page.save(filename, "JPEG")
            image_file_list.append(filename)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Часть 2: распознавание текста по изображениям с помощью OCR
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        #with open(text_file, "a") as output_file:
        for image_file in image_file_list:
        
            #распознать текст как как строку на изображении с помощью tesseract
            text = str(((pytesseract.image_to_string(Image.open(image_file), lang='rus+eng'))))

            #распознанный текст сохраняем в переменной text
            #применяем обработку строк

            #удаляем дефисы при переносе строк
            text = text.replace("-\n", "")

            #удаляем все знаки препинания
            #table = str.maketrans("", "", string.punctuation)
            #text = text.translate(table)

            #output_file.write(text)

            return str(text)


def read_docx(file_path):
    doc = docx.Document(file_path)

    all_paras = doc.paragraphs
    text = ""
    for para in all_paras:
        text += " " + str(para.text)
    return text 