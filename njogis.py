#!usr/bin/env python
# encoding: utf-8

"""
First coded Sept 2016
Intended for use in cropping, alpha-layering, rotation and georeferencing of
single frame records sourced from USGS
"""

import os
import cv2
import numpy as np
import csv
import subprocess
import shutil
from matplotlib import pyplot as plt


# input params
groupname = 'NJOGIS'


# set directories
base_dir = '/home/pam/envirosite/tif'
source_dir = os.path.join(base_dir, 'uncropped' , groupname)
target_dir = os.path.join(base_dir, 'cropped' , groupname)

#define csv extent_dir
csv_dir = os.path.join('/home/pam/envirosite/csv' , groupname)
# define prj dir
prj_dir = os.path.join('/home/pam/envirosite/prj')


##comment out when done testing
# if os.path.exists(target_dir):
#     shutil.rmtree(target_dir)
# os.mkdir(target_dir)
##

# make target_dir
if not os.path.exists(target_dir):
    os.mkdir(target_dir)
# make alpha dir
alpha_dir = os.path.join(target_dir,'alpha')
# if not os.path.exists(alpha_dir):
#     os.mkdir(alpha_dir)
# # # #make binary dir
binary_dir = os.path.join(target_dir,'binary')
# if not os.path.exists(binary_dir):
#     os.mkdir(binary_dir)
#make georef dir
georef_dir =  os.path.join(target_dir, 'georef')
# if not os.path.exists(georef_dir):
#     os.mkdir(georef_dir)
check_dir =  os.path.join(target_dir, 'check')
# if not os.path.exists(check_dir):
#     os.mkdir(check_dir)

code_dir = '/home/pam/envirosite/py'

print 'Folders created ...'

# chdir to source_dir
os.chdir(source_dir)

# get list of tiff from source_dir
tiflist = os.listdir(source_dir)

# set counter var
counter = 0
# set var for outlier trap
review_list = []

ct_list = []

lowerleft_area_list = []
lowerleft_not_area_list = tiflist

def maxareabbox(src):
    ret, thresh = cv2.threshold(src, 0, 255, 0)
    _, contours, _= cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(c) for c in contours]
    max_index = np.argmax(areas)
    cnt = contours[max_index]
    return cv2.boundingRect(cnt)

def dilate(src, windowsize, iterations):
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(windowsize , windowsize)) 
    dilated = cv2.dilate(src,kernel,iterations = iterations)
    return dilated

def rotate(src,angle):
    (h, w) = src.shape[:2]
    center = (w / 2, h / 2)
    # rotate the image with positive angle if clockwise, otherwise use negative for counterclockwise
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rot_img = cv2.warpAffine(src, M, (w, h))
    return rot_img

def maxcontours(src):
    _,contours, _ = cv2.findContours(src,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    areas = [cv2.contourArea(c) for c in contours]
    max_index = np.argmax(areas)
    cnt = contours[max_index]
    return cnt

def sat(src):
    sat = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)[:,:,1]
    return sat
def gray(src):
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    return gray
def hue(src):
    hue = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)[:,:,0]
    return hue
def val(src):
    val = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)[:,:,2]
    return val

def reviewimage(review_list, srcfolder):
    # ch_dir to alpha_dir
    os.chdir(srcfolder)
    print 'Opening ' + str(len(review_list)) + ' selected images for review ...'
    # loop thru list
    for i in review_list:
        # print os.path.join(alpha_dir, i)
        cmd1 = 'gpicview ' + i
        subprocess.Popen(cmd1,shell=True)
        cmd2 = 'pkill gpicview'
        decision = raw_input('Choose rotation options. U : upside-down, L : left, R: right, any key to skip ... ')
        if any(s in decision for s in ('U', 'u')):
            # final rotation
            rot_img_copy = cv2.imread(i, -1)
            (h, w) = rot_img_copy.shape[:2]
            center = (w / 2, h / 2)
            # rotate the image by 180 degrees clockwise
            M = cv2.getRotationMatrix2D(center, -180, 1.0)
            rot_img3 = cv2.warpAffine(rot_img_copy, M, (w, h))
            # write rot_img3 to file
            cv2.imwrite(os.path.join(alpha_dir, i), rot_img3)
            # kill gpicview
            subprocess.call(cmd2,shell=True)

        elif any(s in decision for s in ('L', 'l')): 
            # final rotation
            rot_img_copy = cv2.imread(i, -1)
            (h, w) = rot_img_copy.shape[:2]
            center = (w / 2, h / 2)
            # rotate the image by 90 degrees counter-clockwise
            M = cv2.getRotationMatrix2D(center, 90, 1.0)
            rot_img3 = cv2.warpAffine(rot_img_copy, M, (w, h))
            # write rot_img3 to file
            cv2.imwrite(os.path.join(alpha_dir, i), rot_img3)
            # kill gpicview
            subprocess.call(cmd2,shell=True)

        elif any(s in decision for s in ('R', 'r')): 
            # final rotation
            rot_img_copy = cv2.imread(i, -1)
            (h, w) = rot_img_copy.shape[:2]
            center = (w / 2, h / 2)
            # rotate the image by 90 degrees clockwise
            M = cv2.getRotationMatrix2D(center, -90, 1.0)
            rot_img3 = cv2.warpAffine(rot_img_copy, M, (w, h))
            # write rot_img3 to file
            cv2.imwrite(os.path.join(alpha_dir, i), rot_img3)
            # kill gpicview
            subprocess.call(cmd2,shell=True)
        else:
            # kill gpicview
            subprocess.call(cmd2,shell=True)

def pause():
    programPause = raw_input("Press the <ENTER> key to continue...")


# print ('Processing for cropping, alpha-layering and rotation ...')
# # for i in sorted(tiflist):
# # #uncomment next line if testing only slected files
# for i in [ 'arunjogis120162.tif' ]:

    if os.path.isfile(i):

        # import image in RGB
        img = cv2.imread(i)
        j = i
        
        rot_img = rotate(img, -90)
        print 'Processed: ' + i

        blue, green, red, _=cv2.mean(rot_img)
        print blue, green, red

        if 25 <= blue <= 75:
       ## detect center of ground control markers; use GIMP to arrive at BGR values
            # lower0 = np.array([90,140,90], dtype = "uint8") #first batch
            # upper0 = np.array([130,180,130], dtype = "uint8")
            lower0 = np.array([50,70,50], dtype = "uint8")
            upper0 = np.array([90,120,90], dtype = "uint8")
            markers = cv2.inRange(rot_img, lower0, upper0)
        # binarize and # find contours
            ret2, thresh2 = cv2.threshold(markers, 0, 255, 0)
            _,contours2, _ = cv2.findContours(thresh2,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        # define lists to be used later
            centers = []
            radii = []
            x_list = []
            y_list = []

        # loop only thru desired contours
            for contour in contours2:
            # calculate area
                area = cv2.contourArea(contour)
           
                if area > 0:

                    br = cv2.boundingRect(contour)
                    radii.append(br[2])
                    m = cv2.moments(contour)
                    center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
                    centers.append(center)
                    x_list.append(center[0])
                    y_list.append(center[1])

            # if this is commented then otherwise error on max_y = max(y_list) may ensue; adjust celing and bottom accordingly
                elif area > 50 < 500:
                    br = cv2.boundingRect(contour)
                    radii.append(br[2])
                    m = cv2.moments(contour)
                    center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
                    centers.append(center)
                    x_list.append(center[0])
                    y_list.append(center[1])

        # extract mix and min values from list
            max_y = max(y_list)
            min_y = min(y_list)
            max_x = max(x_list)
            min_x = min(x_list)

            img_crop = rot_img[min_y:max_y +1 , min_x:max_x + 1]
            cv2.imwrite(os.path.join(check_dir, i), img_crop)

        elif blue > 75:
            # lower0 = np.array([80,130,90], dtype = "uint8")
            # upper0 = np.array([110,180,120], dtype = "uint8")
            # lower0 = np.array([80,120,70], dtype = "uint8")
            # upper0 = np.array([120,180,120], dtype = "uint8")
            lower0 = np.array([90,150,90], dtype = "uint8")
            upper0 = np.array([150,200,160], dtype = "uint8")
            markers = cv2.inRange(rot_img, lower0, upper0)
        # binarize and # find contours
            ret2, thresh2 = cv2.threshold(markers, 0, 255, 0)
            _,contours2, _ = cv2.findContours(thresh2,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        # define lists to be used later
            centers = []
            radii = []
            x_list = []
            y_list = []

        # loop only thru desired contours
            for contour in contours2:
            # calculate area
                area = cv2.contourArea(contour)
           
                if area > 0:

                    br = cv2.boundingRect(contour)
                    radii.append(br[2])
                    m = cv2.moments(contour)
                    center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
                    centers.append(center)
                    x_list.append(center[0])
                    y_list.append(center[1])

            # if this is commented then otherwise error on max_y = max(y_list) may ensue; adjust celing and bottom accordingly
                elif area > 50 < 500:
                    br = cv2.boundingRect(contour)
                    radii.append(br[2])
                    m = cv2.moments(contour)
                    center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
                    centers.append(center)
                    x_list.append(center[0])
                    y_list.append(center[1])

        # extract mix and min values from list
            max_y = max(y_list)
            min_y = min(y_list)
            max_x = max(x_list)
            min_x = min(x_list)

            img_crop = rot_img[min_y:max_y +1 , min_x:max_x + 1]
            cv2.imwrite(os.path.join(check_dir, i), img_crop)

#         g = gray(img_crop)
#         lower_bgr = np.array([0,0,0], dtype = "uint8")
#         upper_bgr = np.array([30,20,30], dtype = "uint8")
#         blk_text_mask = cv2.inRange(img_crop, lower_bgr, upper_bgr)
#         # cv2.imwrite(os.path.join(check_dir, i), blk_text_mask)

#         img_text = cv2.bitwise_or(g, g, mask = blk_text_mask)
#         ret, thresh3 = cv2.threshold(img_text, 0, 255, 0)
#         _, contours, _= cv2.findContours(thresh3, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
#         #use the location of the text and the width and height
#         img_crop_copy = img_crop.copy()
#         for cnt in contours:
#             x1,y1,w1,h1 = cv2.boundingRect(cnt)
#             area = cv2.contourArea(cnt)
#             lowerleft = bool(20 < w1 < 40 and 30 < h1 < 60 and 2600 < y1 < 2650)

#             if lowerleft and area > 900:
#                 if j not in lowerleft_area_list:
                
#                     lowerleft_area_list.append(j)

#                 cv2.rectangle(img_crop_copy,(x1,y1),(x1+w1,y1+h1),(0,255,0),2)
#                 if j in lowerleft_not_area_list:
#                     lowerleft_not_area_list.remove(j)

#         if j in lowerleft_area_list:
#             rot_img2 = rotate(img_crop, 180)
#             cv2.imwrite(os.path.join(binary_dir, i), rot_img2)
#         if j in lowerleft_not_area_list:
#             rot_img2 = img_crop
#             cv2.imwrite(os.path.join(binary_dir, i), rot_img2)

# print len(lowerleft_area_list)
# print len(lowerleft_not_area_list)
        
# print("Slideshow alpha images for wrong rotation ...")
# pause()

# os.chdir(binary_dir)
# tiflist2 = os.listdir(binary_dir)
# # for i in sorted(tiflist2):
# for i in ['arunjogis100011.tif']:
#     print i
#     rot_img2 = cv2.imread(i)

#     # lower_gcp = np.array([80,145,90], dtype = "uint8")
#     # upper_gcp = np.array([120,190,130], dtype = "uint8")
#     lower_gcp = np.array([60,80,60], dtype = "uint8")
#     upper_gcp = np.array([100,125,90], dtype = "uint8")
#     # lower_gcp = np.array([80,120,70], dtype = "uint8")
#     # upper_gcp = np.array([120,180,120], dtype = "uint8")
#     gcp = cv2.inRange(rot_img2, lower_gcp, upper_gcp)
#     ret4, thresh4 = cv2.threshold(gcp, 0, 255, 0)
#     dilate4 = dilate(thresh4, 3, 9)
#     # find contours
#     _,contours4, _ = cv2.findContours(dilate4,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

#     # define lists to be used later
#     centers = []
#     radii = []
#     x_list = []
#     y_list = []

#     # rows,columns = thresh4.shape
#     # print 'columns' + str(columns), 'rows' + str(rows)
#     # loop only thru desired contours
#     for contour in contours4:
#         x,y,w,h = cv2.boundingRect(contour) 
#         area = cv2.contourArea(contour)
#         # print  area
#         # if area == 162:
#         #     print x, y
#         # condition = bool(35 < w <= 40 and 35 < h <= 40 and 2600 < x < 2650) or bool(35 < w <= 40 and 35 < h <= 40 and 60 < x < 90)
#         condition = bool(30 < w <= 40 and 30 < h <= 40)
#         if condition:
#             print x, y
#             a = cv2.rectangle(rot_img2,(x,y),(x+w,y+h),(0,0,0),-1)
#             cv2.imwrite(os.path.join(check_dir, i), a)
#             br = cv2.boundingRect(contour)
#             radii.append(br[2])
#             m = cv2.moments(contour)
#             center = (int(m['m10'] / m['m00']), int(m['m01'] / m['m00']))
#             centers.append(center)
#             x_list.append(center[0])
#             y_list.append(center[1])
       
#             # extract mix and min values from list
#             max_y = max(y_list)
#             min_y = min(y_list)
#             max_x = max(x_list)
#             min_x = min(x_list)

#             crop3 = rot_img2[min_y:max_y +1 , min_x:max_x + 1]
#             alpha_img = cv2.cvtColor(crop3, cv2.COLOR_BGR2BGRA)
#             cv2.imwrite(os.path.join(alpha_dir, i), alpha_img)

    ###do this when crop3 above doesnt satisfies the edge cropping
#     gr = gray(crop3)
#     paper = cv2.inRange(gr, 0, 0)
#     img_paper = cv2.bitwise_or(gr, gr, mask=paper)
#     ret, thresh = cv2.threshold(gcp,0, 255, 0)
#     _,contours, _ = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

#     rows, cols, = gr.shape
#     for c in contours:
#         x,y,w,h = cv2.boundingRect(c)
#         upperL = 20 < w < 60 and x == 1 and y == 1
#         lowerL = 20 < w < 60 and x == 1 and y == rows - h - 1
#         upperR = 20 < w < 60 and x == cols - w - 1 and y == -h - 1
#         lowerR = 20 < w < 60 and x == cols - w - 1 and y == 1

#         if (upperL) or (lowerL) or (upperR) or (lowerR) and bool(20 < x < 50 and 2510 < x < 2550):
#             ct_list.append

#     white_bg = np.full(gr.shape, 0, dtype=np.uint8)
#     crop = np.full(gr.shape, 0, dtype=np.uint8)

#     for a in ct_list:
#         crop = cv2.drawCountours(white_bg, [a], 0,(255, 0, 0), -1)
#     _, crop_thresh = cv2.threshold(crop, 0, 255, 0)
#     kernel1 = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
#     dilate1 = cv2.dilate(crop_thresh, kernel1, iterations=5)
#     inv_dilate1 = cv2.bitwise_not(dilate1)
#     masked = cv2.bitwise_or(gr, gr, mask=inv_dilate1)
#     inv_masked = cv2.bitwise_not(masked)
#     img_fg = cv2.bitwise_or(crop3, crop3, mask=masked)
#     alpha = cv2.cvtColor(crop3, cv2.COLOR_BGR2BGRA)    
#     bg = np.full(alpha.shape, 0, dtype=np.uint8)
#     img_fg_alpha = cv2.cvtColor(img_fg, cv2.COLOR_BGR2BGRA)
#     alpha_img = cv2.bitwise_or(img_fg_alpha, bg, mask=masked)
#     cv2.imwrite(os.path.join(alpha_dir, i), alpha_img)      

# print("Slideshow alpha images for wrong rotation ...")
# pause()


# #GEOREFERENCING SECTION


print 'Georeferencing alpha images ...'
# list all TIFs
os.chdir(alpha_dir)
alpha_tifs = os.listdir(alpha_dir)

# set SRID as constant
SRID = '4326'

# loop thru tifs
for tif in sorted(alpha_tifs):
# for tif in ['arupvd090050113.tif']:
    if os.path.isfile(tif):
        k = cv2.imread(tif, -1) #alpha channel = -1
        # k = cv2.imread(tif, 1) #regular image = 1 and grayscale = 0
        rows, cols, bands = k.shape
        ulp_x = '0'
        ulp_y = '0'
        lrp_x = str(cols)
        lrp_y = str(rows)
        
        
        # remove extension in filename
        tifname = os.path.basename(tif)[0:-4] .upper()
        # set source and target filepaths
        sourcefile = os.path.join(alpha_dir, tif)
        targetfile1 = os.path.join(georef_dir, tif)
        
        # read extent data in csv
        with open(os.path.join(csv_dir, groupname + '_extent.csv'), 'r') as csvfile:
            reader = csv.reader(csvfile)
            distinct_rows = []
            for row in reader:
                # remove duplicate rows
                if row not in distinct_rows:
                    distinct_rows.append(row)
            
            for i in distinct_rows:
                # parse and store values
                entity_id,nw_x,nw_y,ne_x,ne_y,se_x,se_y,sw_x,sw_y = i[0:]

                # if (tifname == entity_id and rotation_flag == 'f') :
                #     # assemble gdal_translate command, assuming gdal can be called from command line
                #     cmd0 = "gdal_translate -of GTiff -co COMPRESS=LZW  -a_ullr " + nw_x + ' ' + nw_y + ' ' + se_x + ' ' + se_y + ' -a_srs ' + 'EPSG:'+ SRID + ' '  + sourcefile + ' ' + targetfile1
                #     subprocess.call(cmd0,shell=True)
                
                if ( tifname == entity_id ):
                    cmd1 = 'gdal_translate -of GTiff -co COMPRESS=LZW  '
                    cmd1 = cmd1 + " -gcp " + ulp_x + ' ' + ulp_y + ' ' + nw_x + ' ' + nw_y
                    cmd1 = cmd1 + " -gcp " + lrp_x + ' ' + ulp_y + ' ' + ne_x + ' ' + ne_y
                    cmd1 = cmd1 + " -gcp " + lrp_x + ' ' + lrp_y + ' ' + se_x + ' ' + se_y  
                    cmd1 = cmd1 + " -gcp " + ulp_x + ' ' + lrp_y + ' ' + sw_x + ' ' + sw_y
                    cmd1 = cmd1 + ' -a_srs EPSG:'+ SRID + ' '  + sourcefile + ' ' + targetfile1
                    # call cmd1
                    subprocess.call(cmd1,shell=True)

# make metadata dir and copy
metadata_dir = os.path.join(alpha_dir, 'metadata')
if not os.path.exists(metadata_dir):
    os.mkdir(metadata_dir)
metadata_src = os.path.join(csv_dir, groupname + '_metadata.csv')
metadata_dst = os.path.join(metadata_dir, groupname + '_metadata.csv')
shutil.copy(metadata_src, metadata_dst)
print 'Metadata copied ...'

# make srid dir and copy
srid_dir = os.path.join(alpha_dir, 'inferred_srid')
if not os.path.exists(srid_dir):
    os.mkdir(srid_dir)
srid_src = os.path.join(prj_dir, SRID + '.prj' )
srid_dst = os.path.join(srid_dir, SRID + '.prj')
shutil.copy(srid_src, srid_dst)
print 'SRID definition copied ...'

print 'Total images processed: ' + str(counter)
        
print 'Process done ...'

# # dev only"
os.chdir(code_dir)