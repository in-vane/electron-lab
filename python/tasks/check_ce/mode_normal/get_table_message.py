import re
import time
from .get_similarity import compare_dictionaries


def get_standard_document_as_dict(wb, sheet_name):
    """
    获取吉森标准ce表的表格红色参数信息
    :param standard_excel: 吉森ce表
    :param sheet_name: excel表内的工作表
    :return: 一个字典
    """
    # Load the Excel file
    # wb = openpyxl.load_workbook(standard_excel)
    # Access the specified sheet
    sheet = wb[sheet_name]

    red_text_dict = {}  # Create a dictionary to store the results

    # Traverse each row
    for row in sheet.iter_rows(min_row=1, max_row=sheet.max_row, min_col=1, max_col=sheet.max_column):
        # Assume the table's first column is not empty and starts from the second column
        table_start_column = None
        for cell in row:
            if cell.value is not None and table_start_column is None:
                table_start_column = cell.column

        # If the start of the table is found
        if table_start_column is not None:
            first_cell_value = row[table_start_column - 1].value  # Get the value of the first column of the table
            red_texts = []
            for cell in row[table_start_column:]:
                if cell.font and cell.font.color and cell.font.color.rgb == 'FFFF0000':  # Look for red font
                    red_texts.append(cell.value)  # Add the red font value to the list

            if red_texts:
                # If the key is already in the dictionary, append the new red text value
                if first_cell_value in red_text_dict:
                    red_text_dict[first_cell_value].extend(red_texts)
                else:
                    # Otherwise, create a new key in the dictionary
                    red_text_dict[first_cell_value] = red_texts

    print(red_text_dict)
    red_text_dict = update_key_standard_dict(red_text_dict)
    return red_text_dict


def update_key_standard_dict(data_dict):
    """
    对get_standard_document_as_dict函数获取到字典再处理下，
    的将字典中值为xxxx-xx的键设为CE-sign
    :param data_dict:一个字典
    :return:修改后的字典
    """
    # Define the regex pattern for 'xxxx-xx'
    ce_sign_pattern = re.compile(r'\b\d{4}-\d{2}\b')

    # Create a new dictionary to store updated results
    updated_dict = {}

    # Iterate over items in the original dictionary
    for key, values in data_dict.items():
        # Assume each key only has one value in the list
        if values and ce_sign_pattern.match(values[0]):
            # If the value matches the pattern, change the key to 'CE-sign'
            updated_dict['CE-sign'] = values
        else:
            # Otherwise, keep the original key-value pair
            updated_dict[key] = values

    return updated_dict


def get_client_document_as_dict(doc):
    """
    读取传入的PDF文档对象里面的ce表，转化为字典。
    主要形式是每行的第一个单元为键，而后面的单元作为该键的值，{'第一个单元内容':['第二单元','第三单元']}

    :param doc: 客户的pdf文档对象
    :return: 读取pdf文档里面的ce表，转化为一个字典
    """
    ce_sign_pattern = re.compile(r'\b\d{4}-\d{2}\b')  # 定义正则表达式匹配模式
    ce_sign = None  # 初始化CE标记变量

    page = doc[0]  # 获取第一页
    text = page.get_text()  # 提取整页文本

    # 在整页文本中搜索符合CE标记的模式
    ce_search = ce_sign_pattern.search(text)
    if ce_search:
        ce_sign = ce_search.group(0)  # 如果找到，提取CE标记

    # 初始化字典来存储表格数据
    table_dict = {}

    # 如果找到CE标记，添加到字典中
    if ce_sign:
        table_dict['CE-sign'] = [ce_sign]

    table_dict = remove_none_keys(table_dict)
    table_dict = {k: v for k, v in table_dict.items() if v is not None}
    return table_dict


"""

def get_client_document_as_dict(pdf_path):
  
    ce_sign_pattern = re.compile(r'\b\d{4}-\d{2}\b')  # 定义正则表达式匹配模式
    ce_sign = None  # 初始化CE标记变量
    with fitz.open(pdf_path) as pdf:
        page = pdf[0]  # 获取第一页
        text = page.get_text()  # 提取整页文本

        # 在整页文本中搜索符合CE标记的模式
        ce_search = ce_sign_pattern.search(text)
        if ce_search:
            ce_sign = ce_search.group(0)  # 如果找到，提取CE标记

        # 以下是提取表格数据的尝试性代码
        # Fitz没有专门提取表格的方法，所以这部分需要根据实际PDF内容进行定制
        # 可能需要分析页面文本的布局，手动解析表格数据
        table_dict = {}  # 初始化字典来存储表格数据
        # 代码逻辑需要根据您的PDF结构和数据布局来定制
    # 如果找到CE标记，添加到字典中
    if ce_sign:
        ce_list = []
        ce_list.append(ce_sign)
        table_dict['CE-sign'] = ce_list
    table_dict = remove_none_keys(table_dict)
    return table_dict
"""


def remove_none_keys(dictionary):
    """
    删除字典，键为空的键值对
    :param dictionary: 一个字典
    :return: 修改后的字典
    """
    # 删除字典中键为None的项
    if None in dictionary:
        del dictionary[None]
    return dictionary


def all(wb, work_table, doc):
    # 假设Excel文件已经保存在以下路径
    # 调用函数并打印结果

    red_text_data = get_standard_document_as_dict(wb, work_table)
    print(red_text_data)

    # 调用函数并传入PDF文件的路径
    table_data = get_client_document_as_dict(doc)
    print(table_data)
    start = time.time()
    red_text_data = compare_dictionaries(red_text_data, table_data)
    print(red_text_data)
    end = time.time()
    print(f"对字典进行匹配耗时{end - start}秒")
    return red_text_data
