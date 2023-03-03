import cv2 as cv
from cv2 import imshow, imread
from Shape_matching import img_scaling, shape_match
from Label_detection import label_detection, get_label_placement, draw_label_box, draw_cap_box, single_label_detection, is_label_match
from Liquid_level import get_liquid_level

def Bottle_inspection(file_name, logger):
    img2 = imread(file_name)
    img2 = img_scaling(img2, 0.25)
    img_input = img2.copy()

    # Templates used to compare bottles brands
    img1 = imread("Zdjecia/w_z_b_9.jpg")
    img1 = img_scaling(img1, 0.25)
    img3 = imread("Zdjecia/r_b_7.jpg")
    img3 = img_scaling(img3, 0.25)
    img4 = imread("Zdjecia/s_eg_11.jpg")
    img4 = img_scaling(img4, 0.25)

    # Templates used to compare DrWit bottle labels
    img11 = imread("Bazy/baza1.png")
    img12 = imread("Bazy/baza2.png")
    img13 = imread("Bazy/baza3.png")
    img14 = imread("Bazy/baza4.png")
    img15 = imread("Bazy/baza5.png")
    img16 = imread("Bazy/baza6.png")
    img17 = imread("Bazy/baza7.png")
    img18 = imread("Bazy/baza8.png")
    img19 = imread("Bazy/baza9.png")

    # Scaling template images to the same scale as bottles images
    wit_base = [img11, img12, img13, img14, img15, img16, img17, img18, img18]
    for i in range(0, len(wit_base)):
        wit_base[i] = img_scaling(wit_base[i], 0.25)
    
    # Template used to find DrWIt cap position
    img_wit_cap = imread("Bazy/wit_cap.png")
    img_wit_cap = img_scaling(img_wit_cap, 0.25)

    # Templates used to compareRiviva bottle labels
    img_r_label = imread("Bazy/riviva_label.png")
    img_r_label = img_scaling(img_r_label, 0.25)
    img_r_cap = imread("Bazy/riviva_cap.png")
    img_r_cap = img_scaling(img_r_cap, 0.25)

    # Templates used to compare Somersby bottle main labels
    img_s1 = imread("Bazy/somer1.png")
    img_s2 = imread("Bazy/somer2.png")
    img_s3 = imread("Bazy/somer3.png")
    
    #Somersby labels templates scaled
    somer_base = [img_s1, img_s2, img_s3]
    for i in range(0, len(somer_base)):
        somer_base[i] = img_scaling(somer_base[i], 0.25)

    # Templates used to compare Somersby bottle uper labels
    img_s11 = imread("Bazy/somer11.png")
    img_s12 = imread("Bazy/somer12.png")
    
    #Somersby labels templates scaled
    somer_base_up = [img_s11, img_s12]
    for i in range(0, len(somer_base_up)):
        somer_base_up[i] = img_scaling(somer_base_up[i], 0.25)
    
    # matching bottles shapes and assigning brand
    brand = shape_match(img2, img1, img3, img4)

    if(brand == 1):
        bottle = "DrWit"
    elif(brand == 2):
        bottle = "Riviva"
    elif(brand == 3):
        bottle = "Somersby"
    
    # according to brand consecutive execution functions
    if(brand == 1):
        label_nr = label_detection(img2, brand, wit_base)
        cap_template = img_wit_cap
        
        if(label_nr != -1):
            label_match = True
        else:
            label_match = False

        if(label_match):
            template = wit_base[label_nr]
    
    if(brand == 2):
        cap_template = img_r_cap
        good_match_nr = single_label_detection(img2, img_r_label)
        label_match = is_label_match(good_match_nr)

        if(label_match is True):
            template = img_r_label

    if(brand == 3):
        label_nr = label_detection(img2, brand, somer_base)
        
        if(label_nr != -1):
            label_match = True
        else:
            label_match = False

        if(label_match):
            template = somer_base[label_nr]


    if(label_match):
        top, bottom = get_label_placement(img2, template)
        img_w_box = draw_label_box(img2, top, bottom)
        img_, full = get_liquid_level(img2, img_w_box, brand)
    else:
        img_, full = get_liquid_level(img2, img2, brand)

    if(brand != 3):
        top_c, bottom_c = get_label_placement(img2, cap_template)
        img_processed = draw_cap_box(img2, top_c, bottom_c, img_)
    
    if(brand == 3):
        label_nr = label_detection(img2, brand, somer_base_up)
        
        if(label_nr != -1):
            label_match_up = True
        else:
            label_match_up = False

        if(label_match_up):
            template_up = somer_base_up[label_nr]
            top_up, bottom_up = get_label_placement(img2, template_up)
            img_processed = draw_cap_box(img2, top_up, bottom_up, img_)
        else:
            img_processed = img_

    # text message to user
    logger(f"In the picture is a bottle of {bottle}.")
    if(label_match):{logger("The bottle has a label.")}
    else:{logger("The bottle has no label.")}
    if(full != 0):
        logger(f"There is liquid in the bottle. Liquid level is at {full}% of the bottle height.")
        if(label_match):
            logger("Caution! Given liquid level value may be incorrect, because of possibility of liquid presence behind label.")
    else:
        logger("The bottle is empty.")

    img_input = img_scaling(img_input, 0.66)
    img_processed = img_scaling(img_processed, 0.66)
    return img_input, img_processed

if __name__ == "__main__":
    file_name = "C:/Users/Administrator/Desktop/Zdjecia/r_b_6.jpg"
    img_input, img = Bottle_inspection(file_name, None)
    imshow("Processed image", img)
    cv.waitKey(0)