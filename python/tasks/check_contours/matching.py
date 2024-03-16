import cv2
import numpy as np
from .digital_detection import get_combined_results
from .part_detection import get_contour_image


# 定义一个函数，用来检查一个边框是否在某个圆圈内
def is_inside_circle(circle, bbox):
    (x, y, radius) = circle
    (x_min, y_min, x_max, y_max) = bbox
    center_x, center_y = (x_max + x_min) / 2, (y_max + y_min) / 2
    return np.sqrt((center_x - x) ** 2 + (center_y - y) ** 2) < radius


def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def line_inside_bbox_ratio(line, bbox):
    x1, y1, x2, y2 = line
    xmin, ymin, xmax, ymax = bbox

    inside_first = xmin <= x1 <= xmax and ymin <= y1 <= ymax
    inside_second = xmin <= x2 <= xmax and ymin <= y2 <= ymax

    # 如果两个端点都在bbox外，则比例为0
    if not inside_first and not inside_second:
        return 0

    line_length = calculate_distance((x1, y1), (x2, y2))

    # 如果两个端点都在bbox内，整条线都在bbox内
    if inside_first and inside_second:
        return 1

    # 如果只有一个端点在bbox内，估计在bbox内的线段长度比例
    # 由于我们没有一个精确计算交点的方法，我们可以使用一种简化的估计
    # 这里我们简单地假设大约80%的线在bbox内作为一个启发式方法
    return 0.8


def find_connected_line_to_circle(circle, lines, min_distance_to_connect=5):
    """
    找到与圆圈相连的直线。
    :param circle: 圆圈参数(x, y, radius)。
    :param lines: 所有检测到的直线。
    :param min_distance_to_connect: 判断直线与圆圈连接的最小距离。
    :return: 与圆圈相连的直线列表。
    """
    x, y, r = circle
    connected_lines = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            # 计算直线两端点到圆心的距离
            distance_1 = np.sqrt((x - x1) ** 2 + (y - y1) ** 2)
            distance_2 = np.sqrt((x - x2) ** 2 + (y - y2) ** 2)

            # 如果其中一个端点的距离小于半径加上预设的连接距离，则认为直线与圆圈相连
            if distance_1 < r + min_distance_to_connect or distance_2 < r + min_distance_to_connect:
                connected_lines.append((x1, y1, x2, y2))
                break
    return connected_lines


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


def calculate_center(bbox):
    x_min, y_min, x_max, y_max = bbox
    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2
    return (center_x, center_y)


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


def is_line_inside_bbox(line, bbox):
    x1, y1, x2, y2 = line
    xmin, ymin, xmax, ymax = bbox

    # 检查两个端点是否都在bbox内部
    inside_first = xmin <= x1 <= xmax and ymin <= y1 <= ymax
    inside_second = xmin <= x2 <= xmax and ymin <= y2 <= ymax

    return inside_first and inside_second


def is_point_inside_bbox(point, bbox, margin=0):
    x, y = point
    xmin, ymin, xmax, ymax = bbox
    return (xmin - margin) <= x <= (xmax + margin) and (ymin - margin) <= y <= (ymax + margin)


def find_closest_line_to_bbox(bbox, lines):
    center_point = calculate_center(bbox)
    min_distance = np.inf
    closest_line = None
    margin = 10  # 定义边缘容忍范围为10个像素

    for line in lines:
        x1, y1, x2, y2 = line[0]  # 注意根据实际情况调整直线数据的解包方式
        line_endpoints = (x1, y1, x2, y2)

        # 检查两个端点是否在扩展的bbox内
        inside_first_with_margin = is_point_inside_bbox((x1, y1), bbox, margin)
        inside_second_with_margin = is_point_inside_bbox((x2, y2), bbox, margin)

        # 检查两个端点是否在原始bbox外
        outside_first_without_margin = not is_point_inside_bbox((x1, y1), bbox, -margin)
        outside_second_without_margin = not is_point_inside_bbox((x2, y2), bbox, -margin)

        # 如果两个端点都在边缘容忍范围外，或者一个在内一个在外
        if (outside_first_without_margin and outside_second_without_margin) or \
                (inside_first_with_margin != inside_second_with_margin):
            distance = point_to_line_distance(center_point, line_endpoints)
            if distance < min_distance:
                min_distance = distance
                closest_line = line_endpoints

    return closest_line


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
    max_extension_distance = 500  # 最大延长距离
    extension_distance = 0  # 初始化延长距离计数器
    # 沿反方向延长寻找零件框
    while True:
        current_point += normalized_direction * 10  # 适当调整步长

        # 检查是否碰到零件框
        for contour in contours:
            if cv2.pointPolygonTest(contour, tuple(current_point), False) >= 0:
                return contour  # 找到碰到的零件框

        # 这里可以添加额外的终止条件，例如最大延长距离
        # 更新延长距离计数器
        extension_distance += 10  # 假设每次延长步长为10
        if extension_distance >= max_extension_distance:
            break


def get_results(image):
    # 加载图像并转换为灰度图
    # image = cv2.imread('/home/zhanghantao/tmp/lingjian/image/img1.png')
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用高斯模糊和Canny边缘检测
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    edges = cv2.Canny(blurred_image, 50, 150)
    # 检测圆圈
    circles = cv2.HoughCircles(blurred_image, cv2.HOUGH_GRADIENT, 1, 20,
                               param1=50, param2=30, minRadius=0, maxRadius=0)

    # 使用霍夫变换检测直线
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)

    combined_results = get_combined_results(image)

    # 初始化字典来存储数字和最近直线的配对关系
    digit_to_line_mapping = {}
    filtered_contours = get_contour_image(image)
    image1 = image.copy()
    # 遍历每个识别到的数字
    for idx, (bbox, text, prob) in enumerate(combined_results):
        if prob > 0.3 and text.isdigit():  # 确保识别的文本是数字且置信度足够高
            # 统一格式的边框为 [x_min, y_min, x_max, y_max]
            x_min, y_min, x_max, y_max = bbox
            # 计算数字的中心点
            digit_center = ((x_max + x_min) / 2, (y_max + y_min) / 2)
            # 找到离数字中心点最近的圆圈
            closest_circle = min(circles,
                                 key=lambda c: np.sqrt((c[0] - digit_center[0]) ** 2 + (c[1] - digit_center[1]) ** 2))
            # 找到与这个圆圈相连的直线
            connected_lines = find_connected_line_to_circle(closest_circle, lines)
            # 如果找到相连的直线，选择一个作为箭头（这里可以根据你的逻辑进一步选择哪一条线）
            if connected_lines:
                arrow_line = connected_lines[0]  # 假设选择第一条连线作为箭头

                # 可视化结果（如果需要）
                cv2.line(image, (arrow_line[0], arrow_line[1]), (arrow_line[2], arrow_line[3]), (0, 0, 255), 2)
            # cv2.imwrite('/home/zhanghantao/tmp/lingjian/results/test.png', image)
            # 因为边框格式已经统一，所以我们可以直接使用这些坐标绘制矩形
            cv2.rectangle(image1, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)

            # 在边框上方显示识别的文本
            cv2.putText(image1, text, (int(x_min), int(y_min) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            # cv2.imwrite('/home/zhanghantao/tmp/lingjian/results/result1.png', image1)

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
                # # 使用数字的文本内容和索引作为键，以便在存在多个相同数字时进行区分
                # key = f"{text}_{idx}"
                # # 将最近直线的信息存储为字典的值
                # digit_to_line_mapping[key] = closest_line
# cv2.imwrite('/home/zhanghantao/tmp/lingjian/results/result5.png', image)
