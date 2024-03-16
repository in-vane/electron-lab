import cv2


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

        # Calculate the bounding rect and aspect ratio
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
        fill_ratio = area / (w * h) if w * h > 0 else 0

        # Filter based on aspect ratio and fill ratio
        if aspect_ratio <= max_aspect_ratio and fill_ratio >= min_fill_ratio:
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            if len(approx) >= 1:  # Filter out simple geometries
                filtered_contours.append(cnt)

    return filtered_contours  # or return [largest_contour] if you want to only return the largest one

#
# # Load the image
# file_path = '/home/zhanghantao/tmp/lingjian/image/img2.png'
# image = cv2.imread(file_path)
# filtered_contours=get_contour_image(image)
# # Draw contours on the original image (for visualization)
# contour_image = image.copy()
# cv2.drawContours(contour_image, filtered_contours, -1, (0, 255, 0), 3)
#
# # 假设 'processed_image' 是您处理后的图像变量
# cv2.imwrite('/home/zhanghantao/tmp/lingjian/results/result1.png', contour_image)
