import base64

import cv2
import easyocr
import numpy as np
from paddleocr import PaddleOCR
from shapely.geometry import box  # 使用Shapely库检查两个边框是否重叠


# ===== matching =====
def find_farthest_point_from_bbox(bbox, line):
    """
    找到距离bbox中心最远的直线端点。
    :param bbox: 数字的边框 [x_min, y_min, x_max, y_max]。
    :param line: 直线的两个端点 [x1, y1, x2, y2]。
    :return: 距离bbox中心最远的端点 (x, y)。
    """
    digit_center = calculate_center(bbox)
    point1 = (line[0], line[1])
    point2 = (line[2], line[3])

    dist1 = np.linalg.norm(np.array(digit_center) - np.array(point1))
    dist2 = np.linalg.norm(np.array(digit_center) - np.array(point2))

    return point2 if dist2 > dist1 else point1


def extend_line_from_farthest_point(bbox, line, contours):
    """
    从距离bbox中心最远的直线端点开始延长，找到碰到的第一个零件框。
    """
    # 找到距离数字框较远的端点
    farthest_point = find_farthest_point_from_bbox(bbox, line)

    # 计算延长方向
    if farthest_point == (line[0], line[1]):
        direction = (line[0] - line[2], line[1] - line[3])
    else:
        direction = (line[2] - line[0], line[3] - line[1])

    normalized_direction = direction / np.linalg.norm(direction)

    # 初始化延长点
    current_point = np.array(farthest_point, dtype=float)

    # 沿反方向延长寻找零件框
    while True:
        current_point += normalized_direction * 10  # 适当调整步长

        # 检查是否碰到零件框
        for contour in contours:
            if cv2.pointPolygonTest(contour, tuple(current_point), False) >= 0:
                return contour  # 找到碰到的零件框

        # 这里可以添加额外的终止条件，例如最大延长距离


def point_to_line_distance(point, line):
    """
    计算点到直线的距离。
    :param point: 点的坐标 (x, y)。
    :param line: 直线的两个端点 [(x1, y1), (x2, y2)]。
    :return: 点到直线的距离。
    """
    x0, y0 = point
    x1, y1, x2, y2 = line
    # num = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1)
    den1 = np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    den2 = np.sqrt((x2 - x0) ** 2 + (y2 - y0) ** 2)
    if den1 > den2:
        return den2
    else:
        return den1


def calculate_center(bbox):
    x_min, y_min, x_max, y_max = bbox
    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2
    return (center_x, center_y)


def find_closest_line_to_bbox(bbox, lines):
    center_point = calculate_center(bbox)
    min_distance = np.inf
    closest_line = None

    for line in lines:
        x1, y1, x2, y2 = line[0]  # 注意根据实际情况调整直线数据的解包方式
        line_endpoints = (x1, y1, x2, y2)
        distance = point_to_line_distance(center_point, line_endpoints)
        if distance < min_distance:
            min_distance = distance
            closest_line = line_endpoints

    return closest_line


# ===== part detection =====
def get_contour_image(image, min_area=200, max_aspect_ratio=6, min_fill_ratio=0.1):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Perform edge detection using Canny
    edges = cv2.Canny(blurred_image, 200, 300)

    # Find contours from the edges
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on area (this threshold can be adjusted)
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
    filtered_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue

        # 计算轮廓的边界矩形和长宽比
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
        fill_ratio = area / (w * h) if w * h > 0 else 0

        # 过滤长宽比过大或填充率过小的轮廓
        if aspect_ratio <= max_aspect_ratio and fill_ratio >= min_fill_ratio:
            # 近似轮廓，判断顶点数量
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            if len(approx) >= 1:  # 过滤掉简单几何形状
                filtered_contours.append(cnt)

    return filtered_contours


# ===== digital detection =====
def check_overlap(bbox1, bbox2):
    # 创建两个矩形框
    rect1 = box(bbox1[0], bbox1[1], bbox1[2], bbox1[3])
    rect2 = box(bbox2[0], bbox2[1], bbox2[2], bbox2[3])
    # 返回两个矩形框是否相交
    return rect1.intersects(rect2)


def remove_duplicates(results):
    filtered_results = []
    # 假设results是已经统一格式的边框
    results.sort(key=lambda x: ((x[0][2] - x[0][0]) * (x[0][3] - x[0][1])), reverse=True)
    for current in results:
        keep = True
        current_bbox = current[0]  # 直接使用统一格式的边框
        for other in filtered_results:
            other_bbox = other[0]  # 直接使用统一格式的边框
            # 检查当前边框是否在已有的边框内或反之
            if check_overlap(current_bbox, other_bbox):
                keep = False
                break
        if keep:
            filtered_results.append(current)
    return filtered_results


def get_easy_results(easy_results):
    combined_results = []
    for (bbox, text, prob) in easy_results:
        # EasyOCR返回的bbox是一个四个顶点的列表，格式为：[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        # 我们需要使用unify_bbox_format函数来转换这个格式
        unified_bbox = unify_bbox_format(bbox)
        combined_results.append((unified_bbox, text, prob))
    return combined_results


# 定义一个函数来统一边框格式为[x_min, y_min, x_max, y_max]
def unify_bbox_format(bbox):
    x_min = min([point[0] for point in bbox])
    y_min = min([point[1] for point in bbox])
    x_max = max([point[0] for point in bbox])
    y_max = max([point[1] for point in bbox])
    return [x_min, y_min, x_max, y_max]


# 示例函数，用于从PaddleOCR返回的结果中提取和转换边框格式
def get_paddle_results(paddle_results):
    combined_results = []
    for line in paddle_results:
        for word_info in line:
            # PaddleOCR结果的结构是[[[bbox_coords], (text, confidence)]]
            bbox_coords = word_info[0]
            text, confidence = word_info[1]
            unified_bbox = unify_bbox_format(bbox_coords)
            combined_results.append((unified_bbox, text, confidence))
    return combined_results


def get_combined_results(image):
    # 初始化OCR对象
    paddle_ocr = PaddleOCR(use_angle_cls=False,
                           lang='en',
                           det_db_thresh=0.2,  # 默认值是0.3，根据需要调整
                           det_db_box_thresh=0.2,  # 默认值是0.5，根据需要调整
                           use_gpu=True)  # 根据您的环境选择是否使用GPU
    reader = easyocr.Reader(['en'], gpu=True)
    # 预处理图像
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 应用二值化
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    paddle_results = paddle_ocr.ocr(binary, cls=False)
    # 使用 EasyOCR 进行文本识别
    easy_results = reader.readtext(binary, detail=1, low_text=0.3, text_threshold=0.3, link_threshold=0.2)
    # Get results
    # paddle_results = get_paddle_results(paddle_results)
    easy_results = get_easy_results(easy_results)
    # Combine results and remove duplicates
    # combined_results = paddle_results + easy_results
    combined_results = easy_results
    # combined_results = remove_duplicates(combined_results)
    return combined_results


# 主函数
def check_contours(base64_data):
    # base64转cv2灰度图
    image_data = base64.b64decode(base64_data)
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用高斯模糊和Canny边缘检测
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    edges = cv2.Canny(blurred_image, 50, 150)

    # 使用霍夫变换检测直线
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)

    combined_results = get_combined_results(image)

    # 初始化字典来存储数字和最近直线的配对关系
    filtered_contours = get_contour_image(image)
    image1 = image.copy()
    # 遍历每个识别到的数字
    for idx, (bbox, text, prob) in enumerate(combined_results):
        if prob > 0.3 and text.isdigit():  # 确保识别的文本是数字且置信度足够高
            # 统一格式的边框为 [x_min, y_min, x_max, y_max]
            x_min, y_min, x_max, y_max = bbox

            # 因为边框格式已经统一，所以我们可以直接使用这些坐标绘制矩形
            cv2.rectangle(image1, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)

            # 在边框上方显示识别的文本
            cv2.putText(image1, text, (int(x_min), int(y_min) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            # 寻找最近的直线
            closest_line = find_closest_line_to_bbox(bbox, lines)
            if closest_line:
                part_contour = extend_line_from_farthest_point(bbox, closest_line, filtered_contours)
                if part_contour is not None:
                    # 绘制数字边框
                    cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                    # 绘制最近的直线
                    cv2.line(image, (closest_line[0], closest_line[1]), (closest_line[2], closest_line[3]), (255, 0, 0),
                             2)
                    # 绘制零件框
                    cv2.drawContours(image, [part_contour], -1, (0, 0, 255), 2)

    _, image_buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(image_buffer).decode('utf-8')

    return image_base64
