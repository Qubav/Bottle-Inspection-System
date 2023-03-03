import cv2 as cv
from Shape_matching import img_scaling, lat_hist, bottle_shape_img

# function returns scaled template(for label matching purpose) with width equal to bottle width
# input temp -> template image, img -> image with bottle in which template will be detected
# wasn't used 
def temp_scaling(temp, img):
    img = img.copy()
    temp = temp.copy()
    img = bottle_shape_img(img, 0)
    x_lh = lat_hist(img, 1)
    x = len(x_lh)
    test = -5
    x_l = x_r = test
    for i in range(0, x, 1):
        if x_lh[i] >= 2550:
            x_l = i
            break
    for i in range(1, x, 1):
        if x_lh[x - i] >= 2550:
            x_r = x - i
            break   
    if (x_l == test or x_r == test):  # protection 
        print("Wystapil blad na etapie przycinania obrazu - shape matching")    # tu cos konczacego / zwracajacego 
    width = x_r - x_l
    h, w = img.shape
    scale = width / w
    temp = img_scaling(temp, scale)

    return temp

# function returns input image masted that way, that only bottle shape is not masked with black mask
# input: img -> image with bottle, bg_color -> 0 if backgorund is black, 1 if background is white
def img_mask_adding(img, bg_color):
    img_copy = img.copy()
    img_blured = cv.GaussianBlur(img_copy, (13, 13), cv.BORDER_DEFAULT)
    mask = bottle_shape_img(img_blured, bg_color)
    masked = cv.bitwise_and(img, img, mask = mask)

    return masked

# function finds keypoint on input imgage and on template, then compares then and returns number of matches clasified as good
# input: img -> image with bottle, label -> image with label that we are comparing
def single_label_detection(img, label):
    img = img.copy()
    label = label.copy()
    orb = cv.ORB_create()
    kp_img, des_img = orb.detectAndCompute(img, None)
    kp_label, des_label = orb.detectAndCompute(label, None)
    bf = cv.BFMatcher()
    matches = bf.knnMatch(des_img, des_label, k = 2)
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append([m])
    return len(good)

# function returns value False or True based od number of good matches number
def is_label_match(good_matches_number):

    if(good_matches_number >= 12):
        return True
    else:
        return False

# function returns vale based on which of images of templates matches best or -1 if there is no match
# img -> image with bottle, brand -> nuber that defines brand, -> imgs_ -> list of images with labels
def label_detection(img, brand, imgs_):
    
    if(brand == 1 or brand == 3):  # WIT
        best_match_val = 0
        for i in range(0, len(imgs_)):
            good_number = single_label_detection(img, imgs_[i])
            if(good_number > best_match_val):
                best_match_val = good_number
                best_match = i

        if(is_label_match(best_match_val)):
        
            return best_match
        
        else:

            return -1

# function returns values of image height where template starts and ends
def get_label_placement(img, template):
    img = img.copy()
    template = template.copy()
    h_t, w_t, _ = template.shape
    res = cv.matchTemplate(template, img, cv.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    top_left = min_loc
    top = top_left[1]
    bottom = top + h_t

    return top, bottom

# function draws bounding box around label based on input top and bottom values and bottle calculated width
def draw_label_box(img, top, bottom):
    img = img.copy()
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_masked_gray = img_mask_adding(img_gray, 0)
    middle = int((top + bottom) / 2)

    for i in range(0, img.shape[1]):
        if(img_masked_gray[middle, i] > 0):
            left = i
            break

    for i in range(1, img.shape[1]):
        if(img_masked_gray[middle, img_masked_gray.shape[1] - i] > 0):
            right = img_masked_gray.shape[1] - i
            break

    color = (0, 255, 255)
    thickness = 5
    img1 = cv.line(img, [left, top], [right, top], color, thickness)
    img2 = cv.line(img1, [left, top], [left, bottom], color, thickness)
    img3 = cv.line(img2, [left, bottom], [right, bottom], color, thickness)
    img4 = cv.line(img3, [right, bottom], [right, top], color, thickness)


    return img4

# function draws bounding box around bottle cap
def draw_cap_box(img, top, bottom, img_w_smth):
    img = img.copy()
    img_w_smth = img_w_smth.copy()
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_masked_gray = img_mask_adding(img_gray, 0)
    middle = int((top + bottom) / 2)

    for i in range(0, img.shape[1]):
        if(img_masked_gray[middle, i] > 0):
            left = i
            break

    for i in range(1, img.shape[1]):
        if(img_masked_gray[middle, img_masked_gray.shape[1] - i] > 0):
            right = img_masked_gray.shape[1] - i
            break

    color = (0, 255, 255)
    thickness = 5
    img1 = cv.line(img_w_smth, [left, top], [right, top], color, thickness)
    img2 = cv.line(img1, [left, top], [left, bottom], color, thickness)
    img3 = cv.line(img2, [left, bottom], [right, bottom], color, thickness)
    img4 = cv.line(img3, [right, bottom], [right, top], color, thickness)

    return img4 








