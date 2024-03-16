import pdfplumber
import pandas as pd
import re

# PDF文件路径和页面指定
# pdf_path = '/home/zhanghantao/tmp/lingjian/image/C043268.pdf'
# page_number = 6  # 指定页面


# 定义一个函数来检查序列是否递增
def is_increasing(sequence):
    return all(x < y for x, y in zip(sequence, sequence[1:]))


# 定义一个函数来检查字符串是否包含数字
def contains_number(s):
    return any(char.isdigit() for char in s)


def form_extraction_and_compare(pdf_path, page_number, digit_to_part_mapping):
    results = []  # 用于存储比对结果
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number - 1]
        tables = page.extract_tables()

        for table in tables:
            df = pd.DataFrame(table[1:], columns=table[0])

            if not contains_number(df.iloc[0, 0]):
                df = df.iloc[1:]

            try:
                df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors='coerce').astype(int)
                df = df.dropna(subset=[df.columns[0]])
            except ValueError:
                continue  # 无法转换第一列为整数，跳过此表格

            numbers = df.iloc[:, 0].tolist()
            if is_increasing(numbers):
                for key, value in digit_to_part_mapping.items():
                    # 查找第一列中值等于key的行
                    row = df[df.iloc[:, 0] == int(key)]
                    if not row.empty:
                        third_column_value = row.iloc[0, 2]  # 假设只有一行匹配
                        numbers_in_third_column = re.findall(r'\d+', third_column_value)
                        if numbers_in_third_column:
                            # 将提取的数字（字符串形式）转换为整数列表
                            numbers = [int(num) for num in numbers_in_third_column]
                            # 比对
                            if value['similar_parts_count'] in numbers:
                                results.append((key, True, None, None))  # 匹配成功
                            else:
                                results.append((key, False, value['similar_parts_count'], numbers))  # 匹配失败，返回详细信息
                        else:
                            results.append((key, False, value['similar_parts_count'], []))  # 第三列没有找到数字，返回详细信息
    return results
