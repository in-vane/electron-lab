import os
import base64
from io import BytesIO

import cv2
import fitz
import numpy as np
from .form_extraction import form_extraction_and_compare
from .digital_detection import get_combined_results
from .matching import find_closest_line_to_bbox, extend_line_from_farthest_point
from .part_detection import get_contour_image


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(CURRENT_PATH, "temp.pdf")

def extract_template(image, contour):
    # 根据轮廓找到边界矩形
    x, y, w, h = cv2.boundingRect(contour)
    # 抠出对应的图像区域
    template = image[y:y + h, x:x + w]
    return template


def match_template_in_image(image, template, method=cv2.TM_CCOEFF_NORMED, threshold=0.8):
    # 进行模板匹配
    res = cv2.matchTemplate(image, template, method)
    # 找到匹配度大于阈值的所有位置
    loc = np.where(res >= threshold)
    return loc


def is_template_larger(template, candidate):
    # 检查模板是否大于候选模板
    th, tw = template.shape[:2]
    ch, cw = candidate.shape[:2]
    return tw <= cw and th <= ch


def find_similar_parts_by_template(image, target_contour, all_contours, threshold=0.9):
    # 首先，从目标轮廓抠出模板
    template = extract_template(image, target_contour)
    similar_parts_count = 0

    for contour in all_contours:
        candidate_template = extract_template(image, contour)
        print(f"Candidate size: {candidate_template.shape}, Template size: {template.shape}")
        if not is_template_larger(template, candidate_template):
            # 如果模板大于候选模板，跳过这个轮廓
            continue
            # 现在我们可以安全地进行模板匹配
        res = cv2.matchTemplate(candidate_template, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        if np.any(loc):
            similar_parts_count += 1
    return similar_parts_count


def find_and_count_matches(image, template, threshold=0.8):
    # 进行模板匹配
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    # 通过阈值找到匹配的区域
    loc = np.where(result >= threshold)

    # 创建与结果大小相同的mask，初始化为全0
    match_mask = np.zeros_like(result, dtype=np.uint8)

    # 确保不会超出界限
    for pt in zip(*loc[::-1]):  # loc[::-1] 使得坐标顺序为(x, y)
        if pt[1] < match_mask.shape[0] and pt[0] < match_mask.shape[1]:
            match_mask[pt[1], pt[0]] = 255

    contours, _ = cv2.findContours(match_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return len(contours)


def find_similar_parts(target_contour, all_contours, tolerance=0.01):
    similar_parts_count = 0
    for contour in all_contours:
        # 计算轮廓之间的相似度
        match = cv2.matchShapes(target_contour, contour, 1, 0.0)
        if match < tolerance:
            similar_parts_count += 1
    return similar_parts_count


def get_results(image, image1):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用高斯模糊和Canny边缘检测
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    edges = cv2.Canny(blurred_image, 50, 150)
    # 使用霍夫变换检测直线
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=100, maxLineGap=5)
    # # 绘制直线
    # for line in lines:
    #     x1, y1, x2, y2 = line[0]  # 提取直线的端点坐标
    #     cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # 在图像上绘制直线，这里颜色为红色，线宽为2
    # cv2.imwrite('/home/zhanghantao/tmp/lingjian/results/result1.png', image)
    combined_results = get_combined_results(image)

    filtered_contours = get_contour_image(image)
    contour_image = image.copy()
    cv2.drawContours(contour_image, filtered_contours, -1, (0, 255, 0), 3)

    # 假设 'processed_image' 是您处理后的图像变量
    # cv2.imwrite('/home/zhanghantao/tmp/lingjian/results/result2.png', contour_image)
    # 初始化字典来存储数字和最近直线的配对关系
    digit_to_part_mapping = {}
    # 遍历每个识别到的数字
    for idx, (bbox, text, prob) in enumerate(combined_results):
        if prob > 0.3 and text.isdigit():  # 确保识别的文本是数字且置信度足够高
            # 统一格式的边框为 [x_min, y_min, x_max, y_max]
            x_min, y_min, x_max, y_max = bbox
            # 因为边框格式已经统一，所以我们可以直接使用这些坐标绘制矩形
            cv2.rectangle(image1, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
            # 在边框上方显示识别的文本
            cv2.putText(image1, text, (int(x_min), int(y_min) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            # 确保bbox中的坐标值是整数
            bbox = [int(val) for val in bbox]
            # 绘制数字边框
            cv2.rectangle(image1, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            # 寻找最近的直线
            closest_line = find_closest_line_to_bbox(bbox, lines)
            if closest_line:
                part_contour = extend_line_from_farthest_point(bbox, closest_line, filtered_contours)
                if part_contour is not None:
                    # 如果数字已经在字典中，比较置信度并更新
                    if text in digit_to_part_mapping:
                        # 比较置信度
                        if prob > digit_to_part_mapping[text]['prob']:
                            digit_to_part_mapping[text] = {'part_contour': part_contour, 'prob': prob, 'bbox': bbox,
                                                           'similar_parts_count': 0}
                    else:
                        digit_to_part_mapping[text] = {'part_contour': part_contour, 'prob': prob, 'bbox': bbox,
                                                       'similar_parts_count': 0}
                    # 绘制数字边框
                    cv2.rectangle(image1, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                    # 绘制最近的直线
                    cv2.line(image1, (closest_line[0], closest_line[1]), (closest_line[2], closest_line[3]),
                             (255, 0, 0),
                             2)
                    # 绘制零件框
                    cv2.drawContours(image1, [part_contour], -1, (0, 0, 255), 2)
                else:
                    # 如果未找到零件框，则更新字典中的相应信息
                    digit_to_part_mapping[text] = {'part_contour': None, 'prob': 0, 'bbox': bbox,
                                                   'similar_parts_count': 0}
    for digit, info in digit_to_part_mapping.items():
        if 'part_contour' in info and info['part_contour'] is not None:
            template = extract_template(image, info['part_contour'])
            count = find_and_count_matches(image, template, threshold=0.8)

            digit_to_part_mapping[digit]['similar_parts_count'] = count

    return digit_to_part_mapping


def check_explore_part(img_base64, pdf, page_number):
    image_data = base64.b64decode(img_base64)
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # 加载图像并转换为灰度图
    # image = cv2.imread('img2.png')
    # PDF文件路径和页面指定
    doc = fitz.open(stream=BytesIO(pdf))
    doc.save(PDF_PATH)
    # page_number = 6  # 指定页面
    print(type(page_number))
    page_number = int(page_number)
    print(type(page_number))
    image1 = image.copy()
    digit_to_part_mapping = get_results(image, image1)
    match_results = form_extraction_and_compare(PDF_PATH, page_number, digit_to_part_mapping)

    # # 获取所有的键和对应的'similar_parts_count'值
    # similar_parts_counts = [(key, info['similar_parts_count']) for key, info in digit_to_part_mapping.items()]
    #
    # # 打印所有的键和对应的'similar_parts_count'值
    # for key, similar_parts_count in similar_parts_counts:
    #     print("Key:", key, "Similar parts count:", similar_parts_count)
    # cv2.imwrite('result5.png', image1)
    for key, matched, found, expected in match_results:
        if matched:
            print(f"Key: {key}, Matched: {matched}")
        else:
            print(f"Key: {key}, Matched: {matched}, Found: {found}, Expected in Table: {expected}")

    return match_results