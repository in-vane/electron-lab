import os
import base64
from io import BytesIO

import fitz
import openpyxl
from openpyxl.styles import Border, Side
import win32com.client as win32
from PIL import ImageGrab
import os

from .get_table_message import all

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(CURRENT_PATH, "temp.xlsx")
IMAGE_PATH = os.path.join(CURRENT_PATH, 'temp.png')


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


# 将ecxel转化为图片
def export_excel_range_to_image(excel_path, image_path, sheet_name):
    """
    导出Excel文件中指定工作表的特定范围为图片。

    参数:
    - excel_path: Excel文件的路径。
    - image_path: 生成的图片保存路径。
    - sheet_name: 工作表
    """
    range_string = "A1:H24"
    # 确保Excel应用程序不可见以加快处理速度
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = False
    try:
        # 打开工作簿
        wb = excel.Workbooks.Open(os.path.abspath(excel_path))
        sheet = wb.Sheets(sheet_name)
        # 选择并复制指定范围
        sheet.Range(range_string).CopyPicture(Appearance=1, Format=2)
        # 从剪贴板获取图像
        image = ImageGrab.grabclipboard()
        # 检查剪贴板上是否有图像并保存
        if image:
            image.save(image_path, 'PNG')
            print(f"图片已保存到 {image_path}")
        else:
            print("剪贴板上没有图像。")
    except Exception as e:
        print(f"发生错误：{e}")
    finally:
        # 关闭工作簿和Excel应用程序
        wb.Close(SaveChanges=False)
        excel.Quit()


def checkTags(excel_file, pdf_file):
    work_table = '例2'
    # doc = fitz.open(pdf_file)
    # wb = openpyxl.load_workbook(excel_file)
    doc = fitz.open(stream=BytesIO(pdf_file))
    wb = openpyxl.load_workbook(filename=BytesIO(excel_file))
    wb.save(EXCEL_PATH)
    message_dict = all(wb, work_table, doc)
    change_excel(wb, work_table, message_dict)
    # 将excel转化为图片，保存到IMAGE_PATG
    export_excel_range_to_image(EXCEL_PATH, IMAGE_PATH, work_table)

    # 创建一个内存中的二进制文件对象
    # excel_buffer = BytesIO()
    # 保存 Excel 文件到二进制对象中
    # wb.save(excel_buffer)
    # 将文件指针移至开头
    # excel_buffer.seek(0)
    # 将二进制数据编码为 Base64 字符串
    # excel_base64 = base64.b64encode(excel_buffer.getvalue()).decode('utf-8')
    # 将PNG图片加载为二进制流
    with open(IMAGE_PATH, "rb") as image_file:
        image_data = image_file.read()
    # 将二进制流编码为Base64字符串
    base64_encoded_data = base64.b64encode(image_data)

    # 将Base64字节对象转换为字符串
    image_base64 = base64_encoded_data.decode('utf-8')
    print(image_base64)
    os.remove(EXCEL_PATH)
    os.remove(IMAGE_PATH)
    # Close the workbook
    # wb.close()

    return image_base64


# checkTags('2.xlsx','2.pdf')