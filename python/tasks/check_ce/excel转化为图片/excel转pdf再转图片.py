import jpype
import os
import asposecells
# import fitz
import fitz  # PyMuPDF
import io
import base64
from PIL import Image

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(CURRENT_PATH, "2.xlsx")
IMAGE_PATH = os.path.join(CURRENT_PATH, 'temp.png')
PDF_PATH = os.path.join(CURRENT_PATH, 'temp.pdf')
def convert_excel_sheet_to_pdf(excel_file, sheet_name):
    # 启动JVM
    jpype.startJVM()
    
    from asposecells.api import Workbook, PdfSaveOptions
    # 加载Excel文档
    workbook = Workbook(excel_file)

    # 获取所有工作表的集合
    worksheets = workbook.getWorksheets()

    # 遍历所有工作表
    for sheet in worksheets:
        print(f"excel中的工作表{sheet}")
        # 如果工作表不是要转换的工作表，将其隐藏
        if sheet.getName() != sheet_name:
            sheet.setVisible(False)

    # 设置PDF保存选项
    saveOptions = PdfSaveOptions()
    saveOptions.setOnePagePerSheet(True)

    # 保存为PDF
    workbook.save(PDF_PATH, saveOptions)

    # 关闭JVM
    jpype.shutdownJVM()


def convert_pdf_page_to_image_base64(pdf_path, page_number=0):
    """
    Convert the specified page of a PDF file into a Base64 image string.
    :param pdf_path: Path to the PDF file.
    :param page_number: The number of the page to convert (0-based).
    :return: Base64 encoded string of the image.
    """
    # 打开PDF文件
    doc = fitz.open(pdf_path)

    # 选择PDF的指定页
    page = doc.load_page(page_number)

    # 将选中的页面转换为图片（pix）
    pix = page.get_pixmap()

     # 使用pixmap的samples属性来获取像素数据
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")  # 使用Pillow保存图像数据到BytesIO对象
    img_bytes.seek(0)

    base64_str = base64.b64encode(img_bytes.read()).decode('utf-8')

    # 关闭文档
    doc.close()

    return base64_str





# 将excel转化为pdf，保存到PDF_PATH
convert_excel_sheet_to_pdf(EXCEL_PATH, '例2')
# 将excel转化为pdf，保存到PDF_PATG
base64_str = convert_pdf_page_to_image_base64(PDF_PATH)

