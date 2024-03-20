import jpype
import os
import asposecells
# import fitz

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
# 将pdf的第一页转化图片
def convert_pdf_page_to_image(pdf_path, image_path, page_number=0):
    """
    Convert the specified page of a PDF file into an image.

    :param pdf_path: Path to the PDF file.
    :param image_path: Path where the image will be saved.
    :param page_number: The number of the page to convert (0-based).
    """
    # 打开PDF文件
    doc = fitz.open(pdf_path)

    # 选择PDF的第一页
    page = doc.load_page(page_number)

    # 将选中的页面转换为图片（pix）
    pix = page.get_pixmap()

    # 将图片保存为文件
    pix.save(image_path)

    # 关闭文档
    doc.close()


  # 将excel转化为pdf，保存到PDF_PATH
convert_excel_sheet_to_pdf(EXCEL_PATH, '例2')
# 将excel转化为pdf，保存到PDF_PATG
# convert_pdf_page_to_image(PDF_PATH, IMAGE_PATH)
