import docx
import fitz
import os.path
import ocrmypdf

def read_docx(file_path):
    doc = docx.Document(file_path)

    all_paras = doc.paragraphs
    text = ""
    for para in all_paras:
        text += " " + str(para.text)
    return text 

def ocr_pdf(file_path):
    if not os.path.isfile(file_path):
        print('[+] File not found')
        exit()
    if not file_path.endswith('.pdf'):
        print('[+] Invalid file extension')
        exit()
    
    #ocrmypdf - добавление в файл текстового слоя с распознанным текстом из документа
    try:
        ocrmypdf.ocr(file_path, file_path, deskew = True, language = ['eng', 'rus'], use_threads=True)
    except ocrmypdf.EncryptedPdfERror:
        print("[+] Текст уже имеет текстовый слой")
    finally:
        #fitz - извлечение текста из доков с текстовым слоем
        doc = fitz.open(file_path)

        text_dict = ""
        for current_page in range(len(doc)):
            if doc.load_page(current_page).get_text("text") != "":
                text_dict += doc.load_page(current_page).get_text("text")
        if len(text_dict) > 0:
            return text_dict 
        else:
            print("\n[+] Документ не имеет текстового слоя")