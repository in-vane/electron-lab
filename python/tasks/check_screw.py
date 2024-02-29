import os
import re
import csv
import shutil
import base64
from io import BytesIO

import cv2
import fitz
import pandas as pd
from tabula import read_pdf
from collections import defaultdict
from ppocronnx.predict_system import TextSystem

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(CURRENT_PATH, "temp.pdf")
IMAGE_PATH = os.path.join(CURRENT_PATH, "image")
CSV_PATH = os.path.join(CURRENT_PATH, "selected_table.csv")


def find_target_table_total():
    # 使用Tabula读取PDF中的表格
    df_list = read_pdf(PDF_PATH, pages='all', multiple_tables=True)

    # 查找并提取符合特定格式的表格
    for df in df_list:
        # 检查表头和内容是否符合预期，您可以根据实际情况调整检查逻辑
        if all(x in df.columns for x in ['A', 'B', 'C']) and 'x' in ''.join(df.iloc[:, 1].astype(str)):
            # 这里可以进一步处理DataFrame，保存为CSV文件
            df.to_csv(CSV_PATH, index=False)


# 获取大写英问字符和对应数字
def manage_csv():
    # 尝试读取CSV文件，假设它位于可以访问的路径
    try:
        df = pd.read_csv(CSV_PATH)

        # 保留包含单个英文字符的行
        df_letters = df[df.apply(lambda x: x.str.contains(r'^[A-Za-z]$', regex=True)).any(axis=1)]

        # 保留包含乘号和数字组合的行，并去除乘号，只保留数字
        df_numbers = df[df.apply(lambda x: x.str.contains('x\d+', regex=True)).any(axis=1)]
        df_numbers = df_numbers.applymap(lambda x: re.sub(r'x(\d+)', r'\1', str(x)) if 'x' in str(x) else x)

        # 保留这两行，组合为新的DataFrame
        df_final = pd.concat([df_letters, df_numbers], ignore_index=True)

        # 覆盖原来的CSV文件
        df_final.to_csv(CSV_PATH, index=False)
    except Exception:
        pass


# csv转字典
def read_csv_to_dict():
    result_dict = {}

    with open(CSV_PATH, 'r', encoding='utf-8') as csv_file:
        # 使用 csv.reader 读取 CSV 文件
        csv_reader = csv.reader(csv_file)

        # 读取第一行为字符，第二行为数字
        characters = next(csv_reader)
        numbers = next(csv_reader)

        # 将字符和数字对应存储到字典中
        result_dict = dict(zip(characters, map(int, numbers)))

    return result_dict


# 获取总的螺丝表
def get_total_screw():
    find_target_table_total()
    manage_csv()
    result_dict = read_csv_to_dict()

    return result_dict


# 提取步骤图里的螺丝表
def extract_images_below_steps(doc):
    # 步骤编号的正则表达式，匹配大于0的数字后跟一个点
    step_pattern = re.compile(r'(?<!\.\d)\b(?<!\d\.)[1-9]\d*\.(?!\d)')

    extracted_images = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        # 在Python层面上使用正则表达式找到所有步骤编号
        for match in re.finditer(step_pattern, page.get_text("text")):
            # 转换匹配的文本为坐标
            match_rects = page.search_for(match.group(0))
            for rect in match_rects:
                # 定义步骤编号下方的矩形区域，此处可能需要调整
                clip_rect = fitz.Rect(rect.x0 - 3, rect.y1 - 20, rect.x1 + 800, rect.y1 + 315)
                # 提取该区域的图像
                pix = page.get_pixmap(clip=clip_rect)
                # 定义图像的保存路径
                image_filename = f"step_{page_num + 1}_{int(rect.x0)}_{int(rect.y1)}.png"
                image_filepath = os.path.join(IMAGE_PATH, image_filename)
                # 保存图像
                pix.save(image_filepath)
                extracted_images.append(image_filepath)

    return extracted_images


def recognize_text_in_images(image_paths):
    # Initialize TextSystem for text recognition
    text_sys = TextSystem()

    # 步骤编号的正则表达式，匹配大于0的数字后跟一个点
    step_pattern = re.compile(r'(?<!\.\d)\b(?<!\d\.)[1-9]\d*\.(?!\d)')

    # 存储满足步骤编号格式的文本
    step_texts = []

    # 用于存储更新后的图片路径列表
    updated_image_paths = []

    for image_path in image_paths:
        # 使用 OpenCV 读取图像
        img = cv2.imread(image_path)

        # 进行文字识别
        res = text_sys.detect_and_ocr(img)

        # 提取识别到的文本
        matched = False
        for boxed_result in res:
            # 如果识别到的文本满足步骤编号格式，则添加到列表中
            if step_pattern.match(boxed_result.ocr_text):
                step_texts.append(boxed_result.ocr_text)
                matched = True
                break

        # 如果未满足步骤编号格式，删除图片
        if not matched:
            os.remove(image_path)
        else:
            updated_image_paths.append(image_path)  # 如果满足条件，则保留图片路径

    return updated_image_paths


def get_image_text(extracted_images):
    text_sys = TextSystem()
    pattern = r'(\d+)\s*X\s*([A-Z])'
    # 初始化一个defaultdict来存储总和，这样每个新键默认值为0
    letter_counts = defaultdict(int)

    # 检测并识别文本
    for image_path in extracted_images:
        img = cv2.imread(image_path)
        res = text_sys.detect_and_ocr(img)
        for boxed_result in res:
            # 使用正则表达式匹配文本
            matches = re.findall(pattern, boxed_result.ocr_text)
            # 遍历所有匹配的文本片段
            for number, letter in matches:
                # 累加匹配到的数字到对应的字母上
                letter_counts[letter] += int(number)

    # 将defaultdict转换为普通字
    return dict(letter_counts)


# 获取步骤螺丝
def get_step_screw(doc):
    # 提取步骤下方的图像
    extracted_images = extract_images_below_steps(doc)
    extracted_images = recognize_text_in_images(extracted_images)
    letter_counts = get_image_text(extracted_images)

    return letter_counts


def check_total_and_step(doc):
    count_mismatch = {}  # 数量不匹配的情况
    extra_chars = {}  # 多余的字符
    missing_chars = {}  # 缺少的字符
    result_dict = get_total_screw()
    letter_counts = get_step_screw(doc)

    # 检查两个字典中的数量是否匹配
    for key in letter_counts:
        if key in result_dict:
            if result_dict[key] != letter_counts[key]:
                count_mismatch[key] = {'expected': result_dict[key], 'actual': letter_counts[key]}
                print(f"数量不匹配: {key}, 应有 {result_dict[key]} 个, 实际有 {letter_counts[key]} 个")
        else:
            print(f"多余的字符: {key} 在 result_dict 中不存在")
            extra_chars[key] = letter_counts[key]

    # 检查result_dict是否有letter_counts没有的字符,多余的种类螺丝
    for key in result_dict:
        if key not in letter_counts:
            print(f"缺少的字符: {key} 在 letter_counts 中不存在")
            missing_chars[key] = result_dict[key]

    return count_mismatch, extra_chars, missing_chars


def find_target_table(doc):
    # 获取PDF的页数
    total_pages = doc.page_count
    found_tables = []  # 用来存储找到的表格和对应的页号

    # 遍历每一页
    for page_number in range(1, total_pages + 1):
        df_list = read_pdf(PDF_PATH, pages=page_number, multiple_tables=True, stream=True)
        for df in df_list:
            if df.empty:
                continue
            # 检查表格是否符合预期格式
            if all(x in df.columns for x in ['A', 'B', 'C']) and 'x' in ''.join(df.iloc[:, 1].astype(str)):
                found_tables.append((df, page_number))  # 添加表格及其页号到列表

    return found_tables  # 返回找到的表格和页号列表


def add_annotation_with_fitz(doc, annotations):
    for page_number, texts in annotations.items():
        # 获取页面对象
        page = doc[page_number - 1]  # 页面索引从0开始

        footer_rect = fitz.Rect(0, page.rect.height - 150, page.rect.width, page.rect.height)

        # 在页脚区域添加红色文本
        page.insert_textbox(footer_rect, texts, color=fitz.utils.getColor("red"), fontsize=12,
                            align=fitz.TEXT_ALIGN_LEFT)


# 主函数
def check_screw(file):
    doc = fitz.open(stream=BytesIO(file))
    doc.save(PDF_PATH)
    if not os.path.isdir(IMAGE_PATH):
        os.makedirs(IMAGE_PATH)

    count_mismatch, extra_chars, missing_chars = check_total_and_step(doc)
    found_tables = find_target_table(doc)

    annotations = {}
    print(count_mismatch)

    # 数量不匹配的情况
    if count_mismatch:
        for _, page_number in found_tables:
            mismatch_texts = []
            for key, counts in count_mismatch.items():
                mismatch_text = f"mismatch: {key} count={counts['expected']} step={counts['actual']}"
                mismatch_texts.append(mismatch_text)
            annotations[page_number] = " ".join(mismatch_texts)

    # 螺丝盒缺少种类螺丝的情况
    if extra_chars:
        for _, page_number in found_tables:
            extra_texts = []
            for key, count in extra_chars.items():
                extra_text = f"missing: total {key}={count}"
                extra_texts.append(extra_text)
            annotations[page_number] = " ".join(extra_texts)

    # 螺丝盒多余种类螺丝的情况
    if missing_chars:
        for _, page_number in found_tables:
            missing_texts = []
            for key, count in missing_chars.items():
                missing_text = f"extra: total {key}={count}"
                missing_texts.append(missing_text)
            annotations[page_number] = " ".join(missing_texts)

    add_annotation_with_fitz(doc, annotations)

    # 将文档转换成字节流
    doc_bytes = doc.write()
    # 将字节流进行base64编码
    doc_base64 = base64.b64encode(doc_bytes).decode('utf-8')

    doc.close()
    os.remove(CSV_PATH)
    os.remove(PDF_PATH)
    shutil.rmtree(IMAGE_PATH)

    return doc_base64
