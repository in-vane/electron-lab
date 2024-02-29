from io import BytesIO
import cv2
import fitz
import base64
import numpy as np
from PIL import Image

dpi = 300


def is_vector_page(page):
    """
    判断页面是否是矢量图
    """
    # 获取页面中的矢量元素数量
    vector_count = len(page.get_drawings())
    print(vector_count)
    # 判断矢量元素数量是否超过阈值
    return vector_count > 1000


def page2img(file):
    # 打开PDF文件
    pdf_document = fitz.open(stream=BytesIO(file))

    # 存储超过阈值的页面图片路径
    vector_page_images = []

    # 遍历PDF的每一页
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        # 判断页面是否是矢量图
        if is_vector_page(page):
            # 保存矢量图页面为图片
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            vector_page_images.append(image)

    # 合成所有矢量图页面为一张图片
    total_width = sum(image.width for image in vector_page_images)
    max_height = max(image.height for image in vector_page_images)
    new_image = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for image in vector_page_images:
        new_image.paste(image, (x_offset, 0))
        x_offset += image.width

    image_data = np.array(new_image)

    # 关闭PDF文件
    pdf_document.close()

    return image_data


def compare_explored(file_1, file_2):
    # 读取图像A和B
    image_data_old = page2img(file_1)
    image_data_new = page2img(file_2)
    image_old = cv2.cvtColor(image_data_old, cv2.COLOR_RGB2GRAY)
    image_new = cv2.cvtColor(image_data_new, cv2.COLOR_RGB2GRAY)

    # 初始化SIFT检测器
    sift = cv2.SIFT_create()

    # 在图像B上检测关键点和描述符, len = 5660
    keypoints_old, descriptors_old = sift.detectAndCompute(image_old, None)

    # 设置窗口大小和步长
    SIZE = 500
    window_size = (SIZE, SIZE)
    step = SIZE
    threshold = 0.1  # 相似度阈值

    rec = []

    # 在图像A上滑动窗口
    for y in range(0, image_new.shape[0] - window_size[0] + 1, step):
        for x in range(0, image_new.shape[1] - window_size[1] + 1, step):
            # 提取窗口内的图像
            window = image_new[y:y + window_size[0], x:x + window_size[1]]

            # 检测关键点和描述符
            keypoints_new, descriptors_new = sift.detectAndCompute(window, None)

            # 使用FLANN匹配器进行特征匹配
            if descriptors_new is not None and descriptors_old is not None:
                FLANN_INDEX_KDTREE = 1
                index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
                search_params = dict(checks=50)
                flann = cv2.FlannBasedMatcher(index_params, search_params)
                matches = flann.knnMatch(descriptors_new, descriptors_old, k=2)

                # 计算匹配度
                good_matches = []
                for m, n in matches:
                    if m.distance < 0.7 * n.distance:
                        good_matches.append(m)

                # 如果匹配度大于阈值，则在图像A上标记红框
                print(x, y, len(good_matches))
                if len(good_matches) < threshold * len(keypoints_new):
                    rec.append((x, y))

    image_new_color = cv2.cvtColor(image_new, cv2.COLOR_GRAY2BGR)
    for i, (x, y) in enumerate(rec):
        cv2.rectangle(image_new_color, (x, y), (x + window_size[1], y + window_size[0]), (0, 0, 255), 2)

    _, image_buffer = cv2.imencode('.jpg', image_new_color)
    image_base64 = base64.b64encode(image_buffer).decode('utf-8')

    return image_base64
