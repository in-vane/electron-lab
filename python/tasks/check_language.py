import os
import shutil
import base64
from io import BytesIO

import re
import cv2
import fitz
from langdetect import detect
from ppocronnx.predict_system import TextSystem

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(CURRENT_PATH, "image")
LANGUAGES = ['EN', 'FR', 'NL', 'DE', 'JA', 'ZH', 'ES', 'AR', 'PT']


# 判断单页文本是否为语言目录页。
def find_language_index_page(page_texts):
    # 正则表达式用于匹配字符串末尾的页码
    page_number_pattern = re.compile(r"(\s\d+|\d+)$")
    language_entries_count = 0
    current_pagenum = 0
    directory_information = {}
    is_index = 0

    for i in range(len(page_texts)):
        # 只检查每个元素的前两个字符
        if any(page_texts[i][:2] == lang for lang in LANGUAGES):
            # 检查当前元素是否以页码结束
            language = page_texts[i][:2]
            match = page_number_pattern.search(page_texts[i])
            if match:
                page_number = match.group()
                if (int(page_number) > current_pagenum):
                    language_entries_count += 1
                    current_pagenum = int(page_number)
                    directory_information[language] = int(page_number)
            # 否则，检查下一个元素是否包含页码
            elif i + 1 < len(page_texts):
                next_match = page_number_pattern.match(page_texts[i + 1])
                if next_match:
                    next_page_number = next_match.group()
                    if (int(next_page_number) > current_pagenum):
                        language_entries_count += 1
                        i += 1  # 跳过下一个元素，因为它是页码
                        current_pagenum = int(next_page_number)
                        directory_information[language] = int(next_page_number)
    
    # 如果一个页面上有超过两个匹配项，则认为是语言目录页
    is_index = language_entries_count > 2

    return is_index, directory_information


# 使用OCR技术读取图像中的文本，确定语言目录页。
def get_image_text(extracted_images):
    text_sys = TextSystem()
    language_index_pages = []  # 存储识别为语言目录的页面编号
    directory_information = {}
    has_match_index = False

    # 检测并识别文本
    for index, image_path in enumerate(extracted_images):
        if has_match_index:
            break

        print(f"Processing page: {index + 1}")  # 打印当前处理的PDF页号
        img = cv2.imread(image_path)
        res = text_sys.detect_and_ocr(img)
        page_texts = [boxed_result.ocr_text for boxed_result in res]  # 仅获取识别的文本内容

        # 判断当前页面是否为语言目录页
        is_index, directory = find_language_index_page(page_texts)
        print(is_index, directory)
        if is_index:
            language_index_pages.append(index + 1)  # 页号是从1开始的
            directory_information = directory
            has_match_index = True

    print(f"directory_information: {directory_information}")

    return language_index_pages, directory_information


# pdf转图像
def convert_pdf_to_images(doc):
    extracted_images = []

    # 确保文件夹存在
    if not os.path.exists(IMAGE_PATH):
        os.makedirs(IMAGE_PATH)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        output_image_path = os.path.join(IMAGE_PATH, f"output_page_{page_num}.png")
        pix.save(output_image_path)
        extracted_images.append(output_image_path)

    return extracted_images


# 提取目录
def get_directory(doc):
    # 将PDF页面转换为图像
    extracted_images = convert_pdf_to_images(doc)

    # 从图像中识别文本
    language_index_pages, directory_information = get_image_text(extracted_images)
    print(f"language_index_pages: {language_index_pages}")

    return language_index_pages, directory_information


def extract_text_by_language(doc, language_pages):
    # Initialize the dictionary to hold the text for each language
    language_texts = {}

    # Get the total number of pages in the document
    total_pages = doc.page_count

    # Sort the languages by the starting page number
    sorted_languages = sorted(language_pages.items(), key=lambda item: item[1])

    # Go through each language and its start page
    for i, (language, start_page) in enumerate(sorted_languages):
        # Determine the end page
        # If it's not the last language, the end page is the start page of the next language - 1
        # If it's the last language, the end page is the last page of the document
        end_page = sorted_languages[i + 1][1] - 1 if i + 1 < len(sorted_languages) else total_pages

        # Extract text from the specified page range
        text = ""
        for page_num in range(start_page, end_page + 1):
            page_text = doc[page_num - 1].get_text()  # Page numbers are zero-indexed in PyMuPDF
            text += page_text

        # Add the extracted text to the dictionary
        language_texts[language] = text

    return language_texts


def detect_language_of_texts(texts_by_languages):
    detected_languages = {}

    for language_code, text in texts_by_languages.items():
        try:
            # Detect the language of the text
            detected_language = detect(text)
            detected_languages[language_code] = detected_language
        except Exception as e:
            # If language detection fails, print an error message
            detected_languages[language_code] = f"Error: {str(e)}"

    return detected_languages


def add_annotation_with_fitz(doc, annotations):
    for page_number, texts in annotations.items():
        # 获取页面对象
        page = doc[page_number - 1]  # 页面索引从0开始
        top_right_rect = fitz.Rect(page.rect.width / 2, 30, page.rect.width - 30, 80)

        # 在右上角区域添加红色文本
        page.insert_textbox(top_right_rect, texts, color=fitz.utils.getColor("red"), fontsize=12,
                            align=fitz.TEXT_ALIGN_RIGHT)


def find_mismatched_languages(doc, detected_languages, page_number):
    mismatched = {}

    # Iterate over the detected_languages dictionary
    for key, value in detected_languages.items():
        # Compare the key and value ignoring case, add to mismatched if they don't match
        if key.lower() != value.lower():
            mismatched[key] = value
    # 根据mismatched字典构造注释文本
    # annotations_text = " ".join([f"{key}:{value}" for key, value in mismatched.items()])

    # 将注释文本与页面编号关联
    # annotations = {page_number[0]: annotations_text}
    # add_annotation_with_fitz(doc, annotations)

    return mismatched


# 主函数
def check_language(file):
    doc = fitz.open(stream=BytesIO(file))

    language_pages = get_directory(doc)
    texts_by_languages = extract_text_by_language(doc, language_pages[1])
    detected_languages = detect_language_of_texts(texts_by_languages)

    mismatched_languages = find_mismatched_languages(doc, detected_languages, language_pages[0])
    is_error = False if len(mismatched_languages.keys()) == 0 else True

    # Printing the new dictionary with mismatched languages
    print(f"detected_languages: {detected_languages}")
    print(f"mismatched_languages: {mismatched_languages}")

    doc.close()
    shutil.rmtree(IMAGE_PATH)

    return is_error, mismatched_languages
