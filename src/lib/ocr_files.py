import docx
import fitz
import os.path


def read_docx(file_path) -> str:
    doc = docx.Document(file_path)

    all_paras = doc.paragraphs
    text = ''
    for para in all_paras:
        text += ' ' + str(para.text)
    return text


def read_pdf(file_path) -> str:
    if not os.path.isfile(file_path):
        raise ValueError('File not found')
    if not file_path.endswith('.pdf'):
        raise ValueError('Invalid file extension')

    # fitz - извлечение текста из доков с текстовым слоем
    doc = fitz.open(file_path)

    text_dict = ''
    for current_page in range(len(doc)):
        if doc.load_page(current_page).get_text('text') != '':
            text_dict += doc.load_page(current_page).get_text('text')
    if len(text_dict) > 0:
        return text_dict
    else:
        raise ValueError('В документе не удалось найти текст')
