import cv2
import easyocr
from difflib import SequenceMatcher
# 使用Shapely库检查两个边框是否重叠
from shapely.geometry import box


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


def iou(box1, box2):
    """计算两个边框的交并比"""
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    iou = intersection_area / float(box1_area + box2_area - intersection_area)
    return iou


def similar(a, b):
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, a, b).ratio()


def is_contained_or_overlapping(box1, box2, threshold=0.5):
    """检查边框是否重叠或包含"""
    if iou(box1, box2) > threshold:
        return True
    if (box1[0] >= box2[0] and box1[1] >= box2[1] and box1[2] <= box2[2] and box1[3] <= box2[3]) or \
            (box2[0] >= box1[0] and box2[1] >= box1[1] and box2[2] <= box1[2] and box2[3] <= box1[3]):
        return True
    return False


def is_contained(box1, box2):
    """检查box1是否在box2内"""
    return box1[0] >= box2[0] and box1[1] >= box2[1] and box1[2] <= box2[2] and box1[3] <= box2[3]


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


def check_overlap(bbox1, bbox2):
    # 创建两个矩形框
    rect1 = box(bbox1[0], bbox1[1], bbox1[2], bbox1[3])
    rect2 = box(bbox2[0], bbox2[1], bbox2[2], bbox2[3])
    # 返回两个矩形框是否相交
    return rect1.intersects(rect2)


def get_combined_results(image):
    # 初始化OCR对象
    # paddle_ocr = PaddleOCR(use_angle_cls=False,
    #                        lang='en',
    #                        det_db_thresh=0.2,  # 默认值是0.3，根据需要调整
    #                        det_db_box_thresh=0.2,  # 默认值是0.5，根据需要调整
    #                        use_gpu=True)  # 根据您的环境选择是否使用GPU
    reader = easyocr.Reader(['en'], gpu=True)
    # 预处理图像
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 应用二值化
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # paddle_results = paddle_ocr.ocr(binary, cls=False)
    # 使用 EasyOCR 进行文本识别
    easy_results = reader.readtext(binary, batch_size=5, detail=1, low_text=0.4, text_threshold=0.4, link_threshold=0.3)
    # Get results
    # paddle_results = get_paddle_results(paddle_results)
    easy_results = get_easy_results(easy_results)
    # Combine results and remove duplicates
    # combined_results = paddle_results + easy_results
    combined_results = easy_results
    # combined_results = remove_duplicates(combined_results)
    return combined_results