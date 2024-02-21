from io import BytesIO
import base64
import tempfile
import fitz
import cv2
import numpy as np


def pixmap_to_cv_image(pixmap):
    # 获取图像数据
    image_data = pixmap.samples

    # 转换为numpy数组
    img_array = np.frombuffer(image_data, dtype=np.uint8)
    img_array = img_array.reshape(pixmap.height, pixmap.width, len(pixmap.samples) // (pixmap.width * pixmap.height))

    # 将BGR格式转换为RGB格式
    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

    return img_array


def compare_ce(file_1, file_2):
    # 打开第一个PDF文件
    pdf1 = fitz.open(stream=BytesIO(file_1))
    # 打开第二个PDF文件
    pdf2 = fitz.open(stream=BytesIO(file_2))

    # 获取第一页的对象
    page1 = pdf1[0]
    page2 = pdf2[0]

    # 渲染第一个PDF页面并将其转换为RGB图像
    pix1 = page1.get_pixmap(matrix=fitz.Matrix(4, 4))  # 设置更高的DPI
    img1 = pixmap_to_cv_image(pix1)

    # 渲染第二个PDF页面并将其转换为RGB图像
    pix2 = page2.get_pixmap(matrix=fitz.Matrix(4, 4))  # 设置更高的DPI
    img2 = pixmap_to_cv_image(pix2)

    # 计算两个页面的差异
    difference = cv2.absdiff(img1, img2)
    gray = cv2.cvtColor(difference, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)

    # 找到轮廓并画出红框
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # 增大矩形的大小
        x -= 5
        y -= 5
        w += 10
        h += 10
        cv2.rectangle(img1, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # 将两个页面拼接在一起
    result = np.concatenate((img1, img2), axis=1)

    _, buffer = cv2.imencode('.jpg', result)
    # 将图像数据编码为 Base64 字符串
    image_base64 = base64.b64encode(buffer).decode('utf-8')

    # 关闭所有打开的PDF文件
    pdf1.close()
    pdf2.close()

    return image_base64
