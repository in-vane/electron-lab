import os
import base64
from io import BytesIO

import fitz
import openpyxl
from openpyxl.styles import Border, Side
from PIL import Image, ImageDraw

from .get_table_message import all

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(CURRENT_PATH, "temp.xlsx")


def change_excel(wb, work_table, message_dict):
    """
    该函数主要是为了，呈现错误信息到吉盛标准ce表上
    :param excel: 吉森标准ce表
    :param work_table: ce表中的工作表
    :param message_dict: 错误信息
    :return:
    """
    # 加载工作簿并选择工作表
    # wb = load_workbook(excel)
    sheet = wb[work_table]

    # 用绿色定义边框样式
    # 用绿色定义边框样式
    green_border = Border(
        left=Side(style='thick', color='0000FF'),
        right=Side(style='thick', color='0000FF'),
        top=Side(style='thick', color='0000FF'),
        bottom=Side(style='thick', color='0000FF')
    )

    # 如果message_dict中有'CE-sign'键，处理它的值
    if 'CE-sign' in message_dict:
        ce_values = message_dict['CE-sign']  # 获取'CE-sign'对应的值列表
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value in ce_values:  # 如果单元格的值在ce_values列表中
                    cell.border = green_border  # 更新边框为绿色

    # 遍历工作表中的每一行，更新其他指定的值的边框
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value in message_dict and cell.value != 'CE-sign':  # 排除'CE-sign'键
                red_texts_positions = message_dict[cell.value]  # 获取红色文本位置的列表
                red_texts_count = 0  # 找到的红色文本单元格的计数器

                for row_cell in row:
                    # 检查单元格的字体是否为红色
                    if row_cell.font and row_cell.font.color and row_cell.font.color.type == 'rgb' and row_cell.font.color.value == 'FFFF0000':
                        red_texts_count += 1  # 递增计数器
                        # 如果当前计数在位置列表中，则更新边界
                        if red_texts_count in red_texts_positions:
                            row_cell.border = green_border

    # 保存文件
    # wb.save(EXCEL_PATH)


def sheet_to_image(excel_file, sheet_name, output_image):
    # 加载 Excel 文件
    wb = load_workbook(excel_file)
    # 选择指定名称的工作表
    ws = wb[sheet_name]
    # 创建一个空白图像对象
    img = Image.new('RGB', (1000, 600), color='white')
    # 获取图像对象的绘图板
    draw = ImageDraw.Draw(img)

    # 将工作表中的内容绘制到图像上
    for row in ws.iter_rows():
        for cell in row:
            # 在图像上绘制单元格内容
            draw.text((cell.column * 50, cell.row * 20), str(cell.value), fill='black')

    # 保存图像到文件
    img.save(output_image)


def checkTags(excel_file, pdf_file):
    work_table = '例2'
    # doc = fitz.open(pdf_file)
    # wb = openpyxl.load_workbook(excel_file)
    doc = fitz.open(stream=BytesIO(pdf_file))
    wb = openpyxl.load_workbook(filename=BytesIO(excel_file))
    # wb.save(EXCEL_PATH)
    message_dict = all(wb, work_table, doc)
    change_excel(wb, work_table, message_dict)

    # # 将文档转换成字节流
    # wb_bytes = wb.write()
    # # 将字节流进行base64编码
    # wb_base64 = base64.b64encode(wb_bytes).decode('utf-8')

    # 创建一个内存中的二进制文件对象
    excel_buffer = BytesIO()
    # 保存 Excel 文件到二进制对象中
    wb.save(excel_buffer)
    # 将文件指针移至开头
    excel_buffer.seek(0)
    # 将二进制数据编码为 Base64 字符串
    excel_base64 = base64.b64encode(excel_buffer.getvalue()).decode('utf-8')

    # os.remove(EXCEL_PATH)
    # Close the workbook
    # wb.close()
    
    return excel_base64