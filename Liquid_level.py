import cv2 as cv
import numpy as np
from Shape_matching import lat_hist
from Label_detection import img_mask_adding

# INPUT IMAGE MUST BE GRAY AND ALREDY MASKED(bottle contour/shape)
# function returns coordinates of top left and bottom roght corrners of rectangle that contains bottle
def get_position(img):
    x_lh = lat_hist(img, 1)
    x = len(x_lh)
    y_lh = lat_hist(img, 0)
    y = len(y_lh)
    test = -5
    x_l = x_r = y_t = y_b = test
    for i in range(0, x, 1):
        if x_lh[i] >= 2550:
            x_l = i
            break
    for i in range(1, x, 1):
        if x_lh[x - i] >= 2550:
            x_r = x - i
            break   
    for i in range(0, y, 1):
        if y_lh[i] >= 2550:
            y_t = i
            break
    for i in range(1, y, 1):
        if y_lh[y - i] >= 2550:
            y_b = y - i
            break
    if (x_l == test or x_r == test or y_t == test or y_b == test):  # protection
        print("Wystapil blad na etapie przycinania obrazu - get_position")    # tu cos konczacego / zwracajacego 
    top_left = [x_l, y_t]
    bottom_right = [x_r, y_b]

    return top_left, bottom_right

# INPUT IMAGE MUST BE IN BGR
# function returns masked image that shows rectangle inlcuding input images part, rectangles height is equal to the height of bottle, and width is equal to input precentage of bottle width
def mask_narrow_rectangle(img, w_percent, img_masked_gray):
    img = img.copy()
    top_left, bottom_right = get_position(img_masked_gray)
    bottle_width = bottom_right[0] - top_left[0]
    w = int(bottle_width * w_percent / 100)
    tl0 = top_left[0] + bottle_width / 2 - w / 2
    br0 = bottom_right[0] - bottle_width / 2 + w / 2
    top_left[0] =  int(tl0)
    bottom_right[0] = int(br0)
    blank = np.zeros((img_masked_gray.shape), dtype=np.uint8)
    mask = cv.rectangle(blank, top_left, bottom_right, (255, 255, 255), -1)
    masked = cv.bitwise_and(img, img, mask = mask)

    return masked

# INPUT IMAGE MUST BE IN BGR
# function returns numer that defines what is the color of the liquid
def get_liquid_color(img, img_masked_gray, brand):
    img = img.copy()
    n_0_p_c = cv.countNonZero(img_masked_gray)
    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    up_yellow = np.array([36, 255, 255])
    bot_yellow = np.array([18, 160, 85])
    up_green = np.array([70, 255, 255])
    bot_green = np.array([35, 50, 50])
    image_yellow = cv.inRange(img_hsv, bot_yellow, up_yellow)
    w_p_c_yellow = cv.countNonZero(image_yellow)
    image_green = cv.inRange(img_hsv, bot_green, up_green)
    w_p_c_green = cv.countNonZero(image_green)
    if(brand == 1):
        if(w_p_c_green < 0.02 * n_0_p_c and w_p_c_yellow < 0.02 * n_0_p_c):
            liquid_color = 0
        elif(w_p_c_green > w_p_c_yellow):
            liquid_color = 1
        elif(w_p_c_yellow > w_p_c_green):
            liquid_color = 2
    if(brand == 2):
        if(w_p_c_yellow < 0.02 * n_0_p_c):
            liquid_color = 0
        else:
            liquid_color = 2
    if(brand == 3):
        if(w_p_c_green < 0.02 * n_0_p_c):
            liquid_color = 0
        else:
            liquid_color = 1
    
    return liquid_color

# Input IMG must be BGR
# function returns image with marked liquid level and percentage of bottle height that liquid level reaches
def get_liquid_level(img, img_w_label_box, brand):
    img = img.copy()
    img_w_label_box = img_w_label_box.copy()
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_masked_gray = img_mask_adding(img_gray, 0)
    color = get_liquid_color(img, img_masked_gray, brand)
    if(color == 0):

        return img_w_label_box, 0

    else:
        img_masked = mask_narrow_rectangle(img, 15, img_masked_gray)
        img_hsv = cv.cvtColor(img_masked, cv.COLOR_BGR2HSV)
        tl, br = get_position(img_masked_gray)
        left = tl[0]
        right = br[0]
        top = tl[1]
        bottom = br[1]
        #Colors HSV valuse defintion
        up_yellow = np.array([36, 255, 255])
        bot_yellow = np.array([18, 160, 85])
        up_green = np.array([89, 255, 255])
        bot_green = np.array([36, 50, 85])

        if(color == 2):
            img_one_color = cv.inRange(img_hsv, bot_yellow, up_yellow)

        elif(color == 1):
            img_one_color = cv.inRange(img_hsv, bot_green, up_green)
        
        kernel = (19, 19)
        img_open = cv.morphologyEx(img_one_color, cv.MORPH_OPEN, kernel)
        y_lh = lat_hist(img_open, 0)

        for i in range(0, len(y_lh), 1):
            if(y_lh[i] > max(y_lh) * 0.4):
                liquid_height = i
                break
        full = int((liquid_height - bottom) / (top - bottom) * 100)

        for i in range(0, img.shape[1]):
            if(img_masked_gray[liquid_height, i] > 0):
                left = i
                break

        for i in range(1, img.shape[1]):
            if(img_masked_gray[liquid_height, img_masked_gray.shape[1] - i] > 0):
                right = img_masked_gray.shape[1] - i
                break

        start_point = [left, liquid_height]
        end_point = [right, liquid_height]
        color = (0, 0, 255)
        thickness = 10

        img_w_line = cv.line(img_w_label_box, start_point, end_point, color, thickness)

        return img_w_line, full