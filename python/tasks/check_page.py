from io import BytesIO
import base64
import fitz
import re


def annotate_page_number_issues(file, printed_page_numbers, physical_page_numbers):
    doc = fitz.open(stream=BytesIO(file))

    # 检查页码问题
    issues = check_page_number_issues(printed_page_numbers, physical_page_numbers)

    # 在有问题的页面上添加注释
    for issue_page_num in issues:
        # 找到对应的物理页码
        physical_page_index = physical_page_numbers[issue_page_num - 1]
        page = doc.load_page(physical_page_index - 1)
        footer_rect = fitz.Rect(0, page.rect.height - 50, page.rect.width, page.rect.height)

        # 在页脚区域添加红色文本
        if issue_page_num % 2 == 0:
            page.insert_textbox(footer_rect, "Page error", color=fitz.utils.getColor("red"), fontsize=12,
                                align=fitz.TEXT_ALIGN_LEFT)
        else:
            page.insert_textbox(footer_rect, "Page error", color=fitz.utils.getColor("red"), fontsize=12,
                                align=fitz.TEXT_ALIGN_RIGHT)

    # 将文档转换成字节流
    doc_bytes = doc.write()

    # 将字节流进行base64编码
    doc_base64 = base64.b64encode(doc_bytes).decode('utf-8')

    return doc_base64, issues


def check_page_number_issues(printed_page_numbers, physical_page_numbers):
    issues = []  # 初始化问题列表
    start_index = None  # 找到第一个非None打印页码的索引
    correct_page_numbers = printed_page_numbers.copy()  # 创建正确页码的副本以进行修改

    # 查找第一个非None打印页码的索引
    for index, page_number in enumerate(printed_page_numbers):
        if page_number is not None:
            start_index = index
            break

    # 如果找到了有效的起始页码
    if start_index is not None:
        # 生成从第一个有效数字开始的连续页码序列
        expected_number = printed_page_numbers[start_index]
        for i in range(start_index, len(printed_page_numbers)):
            correct_page_numbers[i] = expected_number
            expected_number += 1

    # 比较实际页码与正确页码，记录不一致的物理页码
    for i in range(len(printed_page_numbers)):
        if printed_page_numbers[i] != correct_page_numbers[i]:
            issues.append(physical_page_numbers[i])

    return issues


def extract_page_numbers(doc):
    printed_page_numbers = []  # 初始化打印页码列表
    total_pages = len(doc)  # 获取PDF的总页数

    # 生成物理页码列表，从1开始到总页数
    physical_page_numbers = list(range(1, total_pages + 1))

    # 假设我们想要扩大页脚区域的覆盖范围
    footer_height = 70  # 从页面底部向上100个单位，增加页脚区域的高度

    for page_num in range(total_pages):
        page = doc.load_page(page_num)  # 加载当前页

        # 定义页脚区域，从页面底部向上100个单位
        footer_rect = fitz.Rect(0, page.rect.height - footer_height, page.rect.width, page.rect.height)

        # 从页脚区域提取文本
        footer_text = page.get_text("text", clip=footer_rect)

        # 使用正则表达式查找所有数字
        numbers = re.findall(r'\d+', footer_text)

        # 如果当前页页脚区域有数字，则假设最大的数字是页码
        if numbers:
            probable_page_number = max(numbers, key=int)
        else:
            # 如果没有找到数字，将None添加到列表中
            probable_page_number = None

        printed_page_numbers.append(probable_page_number)

    # 将打印页码列表中的元素转换为整数，对于None值保持不变
    printed_page_numbers = [int(item) if item is not None else None for item in printed_page_numbers]

    return printed_page_numbers, physical_page_numbers


# 示例用法
def check_page(file):
    doc = fitz.open(stream=BytesIO(file))

    printed_page_numbers, physical_page_numbers = extract_page_numbers(doc)
    print(printed_page_numbers)
    print(physical_page_numbers)
    doc_base64, issues = annotate_page_number_issues(file, printed_page_numbers, physical_page_numbers)

    doc.close()

    return doc_base64, issues
