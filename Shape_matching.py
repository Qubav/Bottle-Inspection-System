import cv2 as cv
import numpy as np

# Lateral Histogram
# function return array of lateral histogram valuse
# type = 0 for pixel values sum in rows, from top to bottom --> Y
# type = 1 for pixel values sum in columns, from left to right --> X
def lat_hist(img, type):  
        x = img.shape[type]
        lh = np.zeros(x, dtype = int)
        for i in range(0, x, 1):
            if type == 1:
                lh[i] = sum(img[::1, i])
            elif type == 0:
                lh[i] = sum(img[i,::1])
        
        return lh

# function returns scaled image
# scale - scale that will be aplied to image
def img_scaling(img, scale):
    width = int(img.shape[1] * scale)
    height = int(img.shape[0] * scale)
    size = (width, height)

    return cv.resize(img, size, interpolation=cv.INTER_AREA)

# function returns image scaled to a degree that bottle width is equal to withd given as input
# width = nuber of pixels that bottle witdh will be after scaling
def bottle_width_setting(img, width):
    img = img.copy()
    x_lh = lat_hist(img, 1)
    x = len(x_lh)
    x_l = 0
    x_r = 0
    for i in range(0, x, 1):
        if x_lh[i] >= 2550:
            x_l = i
            break
    for i in range(1, x, 1):
        if x_lh[x - i] >= 2500:
            x_r = x - i
            break
    width_w = x_r - x_l
    scale = width / width_w
    img_scaled = img_scaling(img, scale)

    return img_scaled

# function return white bottle shape on blank background
# bg_color = 0 for black background
# bg_color = 1 for white background
def bottle_shape_img(img, bg_color):
    img = img.copy()
    if (bg_color == 0):
        ret, thresh = cv.threshold(img, 35, 255, cv.THRESH_BINARY)
    elif (bg_color == 1):
        ret, thresh = cv.threshold(img, 240, 255, cv.THRESH_BINARY)
    cnt, hier = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
    blank = np.zeros((img.shape), dtype=np.uint8)
    x = len(cnt) - 1
    if (x < 0):
        print("Error connected with contour has occurred!")
    shape_img = cv.fillPoly(blank, [cnt[x]], (255, 255, 255))
    
    return shape_img

# function return cropped image with bottle and specified distance of image from every side
# img is already processed image --> bottle shape 
# percent is what percentage value of height/width(higher value) will be left on each side of bottle shape in process of cutting out important part
def img_crop_shape_match(img, percent):
    img = img.copy()
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
        print("Error alongside image cropping has occured!") 
    width = x_r - x_l
    height = y_b - y_t
    if (height > width):
        add_v = height * percent / 100
    elif (height <= width):
        add_v = width * percent / 100
    x_r = int(x_r + add_v)
    x_l = int(x_l - add_v)
    y_b = int(y_b + add_v)
    y_t = int(y_t - add_v)
    if (y_t < 0):   # protection in case value would be negative or higher than image shape
        y_t = 0
    if (y_b > img.shape[0]):
        y_b = img.shape[0]
    if (x_l < 0):
        x_l = 0
    if (x_r > img.shape[1]):
        x_r = img.shape[1]
    cropped_img = img[y_t:y_b, x_l:x_r]

    return cropped_img

# function return image prepared to be used in shape matcing
# input image must be in BRG scale
def img_prep_shape_match(img, bg_color, percent):
    img = img.copy()
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img = cv.GaussianBlur(img, (13, 13), cv.BORDER_DEFAULT) 
    img = bottle_shape_img(img, bg_color)
    img = img_crop_shape_match(img, percent)
    img = bottle_width_setting(img, 160)
    kernel = np.ones((7, 7), np.uint8)
    img = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)

    return img

# function returns order number of most matching template
# INPUT IMAGES MUST BE IN GREY SCALE   
# img -> img that is being classified, tempx -> templates that will be used to match shape
def shape_match(img, temp1, temp2, temp3):
    img = img.copy()
    temp1 = temp1.copy()
    temp2 = temp2.copy()
    temp3 = temp3.copy()
    img = img_prep_shape_match(img, 0, 3)
    temp1 = img_prep_shape_match(temp1, 0, 3)
    temp2 = img_prep_shape_match(temp2, 0, 3)
    temp3 = img_prep_shape_match(temp3, 0, 3)
    temps = [temp1, temp2, temp3]
    diff = []
    for i in range(0, 3, 1):
        diff.append(cv.matchShapes(img, temps[i], 1, 0.0))
    min_diff = min(diff)
    for i in range(0, len(diff), 1):
        if diff[i] == min_diff:
            x = i + 1
            break
    
    return x









