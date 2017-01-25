#!usr/bin/env python
# encoding: utf-8

import cv2
import numpy as np

# path = 'home/pam/share_download/opencv_logo.jpg'

# img = cv2.imread(path,0)
# img = cv2.medianBlur(img,5)
# cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

# circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20, 50,30,0,0)

# circles = np.uint16(np.around(circles))
# for i in circles[0,:]:
#     # draw the outer circle
#     cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
#     # draw the center of the circle
#     cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)

# cv2.imshow('detected circles',cimg)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
   
import cv2
import numpy as np
import sys

if __name__ == '__main__':
    print(__doc__)

    try:
        fn = sys.argv[1]
    except IndexError:
        fn = "home/pam/share_download/opencv_logo.jpg"

    src = cv2.imread(fn, 1)
    img = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    img2 = cv2.medianBlur(img, 5)
    cimg = src.copy() # numpy function

    circles = cv2.HoughCircles(img2, cv2.HOUGH_GRADIENT, 1, 10, np.array([]), 100, 30, 1, 30)

    if circles is not None: # Check if circles have been found and only then iterate over these and add them to the image
        a, b, c = circles.shape
        for i in range(b):
            cv2.circle(cimg, (circles[0][i][0], circles[0][i][1]), circles[0][i][2], (0, 0, 255), 3, cv2.LINE_AA)
            cv2.circle(cimg, (circles[0][i][0], circles[0][i][1]), 2, (0, 255, 0), 3, cv2.LINE_AA)  # draw center of circle

        cv2.imshow("detected circles", cimg)

    cv2.imshow("source", src)
    cv2.waitKey(0)