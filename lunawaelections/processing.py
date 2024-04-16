from skimage.metrics import structural_similarity as ssim
from django.conf import settings
import concurrent.futures
import json, cv2, os
import numpy as np
import itertools

def get_reference():
    ref = cv2.imread(os.path.join(settings.REFERENCE_ROOT, 'ballot_a3.jpg'), cv2.IMREAD_GRAYSCALE)
    shape = ref.shape
    
    bbox_data = json.load(open(os.path.join(settings.REFERENCE_ROOT, 'boxes_coor.json')))
    (x1, y1), (x2, y2) = bbox_data['Sign']['sign1']
    p, q, r, s = min(y1,y2), max(y1,y2), min(x1,x2), max(x1,x2)
    
    crop_ref = ref[p:q, r:s]
    _, bin_ref = cv2.threshold(ref, 160, 255, cv2.THRESH_BINARY)

    return bbox_data, shape, crop_ref, bin_ref, (p, q, r, s)

def sort_points(points):
    centroid = np.mean(points, axis=0)
    angles = np.arctan2(points[:, 1] - centroid[1], points[:, 0] - centroid[0])
    sorted_indices = np.argsort(angles)
    sorted_points = points[sorted_indices]
    return sorted_points.astype(np.float32)
    
def find_max_quad(contour):
    max_area, max_quad = -1, None
    
    for quad_points in itertools.combinations(contour, 4):
        quad_points = np.array(quad_points)
        area = cv2.contourArea(quad_points)
        if area > max_area: 
            max_area, max_quad = area, quad_points

    if max_quad is not None: max_quad = sort_points(max_quad.reshape(4, 2))
    return max_quad

def get_contour(image):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour = max(contours, key=cv2.contourArea)
    epsilon = 0.01 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    hull = cv2.convexHull(approx)
    max_quad = find_max_quad(hull)
    return max_quad

def wrap_image(image, max_quad):
    x, y, w, h = cv2.boundingRect(max_quad)
    tmp, incorrect = shape, False
    if w>h:
        tmp = (shape[1], shape[0])
        incorrect = True
    
    target_points = np.array([[0, 0], [tmp[1], 0], [tmp[1], tmp[0]], [0, tmp[0]]], dtype=np.float32)
    perspective_matrix = cv2.getPerspectiveTransform(max_quad, target_points)
    warped_image = cv2.warpPerspective(image, perspective_matrix, (tmp[1], tmp[0]))

    if incorrect:
        warped_image1 = cv2.rotate(warped_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        crop_wrp1 = warped_image1[p:q, r:s]
        ssim_score1 = ssim(crop_wrp1, crop_ref)

        warped_image2 = cv2.rotate(warped_image, cv2.ROTATE_90_CLOCKWISE)
        crop_wrp2 = warped_image2[p:q, r:s]
        ssim_score2 = ssim(crop_wrp2, crop_ref)
        
        warped_image = warped_image1 if ssim_score1 > ssim_score2 else warped_image2

    warped_image1 = warped_image
    crop_wrp1 = warped_image1[p:q, r:s]
    ssim_score1 = ssim(crop_wrp1, crop_ref)

    warped_image2 = cv2.rotate(cv2.rotate(warped_image, cv2.ROTATE_90_CLOCKWISE), cv2.ROTATE_90_CLOCKWISE)
    crop_wrp2 = warped_image2[p:q, r:s]
    ssim_score2 = ssim(crop_wrp2, crop_ref)
    
    warped_image = warped_image1 if ssim_score1 > ssim_score2 else warped_image2
    return warped_image

def img_proc(name, threshold):
    image = cv2.imread(name, cv2.IMREAD_GRAYSCALE)
    _, bin_img = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    max_quad = get_contour(bin_img)
    if max_quad is None: return None, False, 0
        
    image = wrap_image(image, max_quad)
    _, bin_img = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    
    sim = ssim(bin_img, bin_ref)
    mse = ((bin_img - bin_ref) ** 2).mean()
    psnr = cv2.PSNR(bin_img, bin_ref)
    score = sim/0.35 + psnr/5 - mse/0.3
    validity = True # if score>1.2 else False
    # print(f'{threshold}, sim: {sim}, mse: {mse}, psnr: {psnr}, score: {score}')
    return image, validity, score

def check_valid(name):
    thresholds = [160, 155, 165, 150, 170, 145, 175, 140, 180, 135, 185, 130, 190, 125, 200]
    final_image, max_score = None, -1

    for thres in thresholds:
        image, valid, score = img_proc(name, thres)
        if valid and score > max_score:
            max_score = score
            final_image = image

    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     futures = {executor.submit(img_proc, name, thres): thres for thres in thresholds}
    #     for future in concurrent.futures.as_completed(futures):
    #         image, valid, score = future.result()
    #         if valid and score > max_score:
    #             max_score = score
    #             final_image = image
                
    # print(max_score)
    return final_image

def get_member(image, sub_value):
    if image is not None and sub_value is not None:
        cropped_image = image[sub_value[0][1]:sub_value[1][1], sub_value[0][0]:sub_value[1][0]]
        _, binary_image = cv2.threshold(cropped_image, 160, 255, cv2.THRESH_BINARY)
        if np.mean(binary_image == 0) > 0.3 : return True
    return False

def draw_bbox(image):
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    outliers, color = [], {}
    for key, values in bbox_data.items():
        for sub_key, sub_value in values.items():
            color = (0, 0, 0)
            if len(key) == 1:
                color = (0, 0, 255)
                if sub_key.isdigit():
                    color = (255, 0, 0)
                    if get_member(image, sub_value):
                        outliers.append(sub_key)
                        color = (0, 255, 0)
            cv2.rectangle(image, sub_value[0], sub_value[1], color, 5)
    
    return image, outliers

def img_display(img, name='Image'):
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, (534, 756))
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

bbox_data, shape, crop_ref, bin_ref, (p, q, r, s) = get_reference()

if __name__ == '__main__':
    file_name = 'ballot_a3.jpg' # 'ballot_3d9c889f0fc3ec64_20240415_235845.jpg'
    image = check_valid(file_name)
    if image is not None:
        image, members = draw_bbox(image)
        img_display(image, file_name)
        print(members)

    # for i in range(10):
    #     image = check_valid(f'../Data/test_{i+1}.jpg')
    #     if image is not None: img_display(draw_bbox(image)[0], file_name)