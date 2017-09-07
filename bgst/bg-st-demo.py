# -*- coding: utf-8 -*-
"""
视频背景消除
"""

import numpy as np
import cv2
cv2.ocl.setUseOpenCL(False)
cap = cv2.VideoCapture(0)
# mog2
#fgbg = cv2.createBackgroundSubtractorMOG2()
#
# knn
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
#fgbg = cv2.createBackgroundSubtractorKNN()
fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()
#fgbg = cv2.createBackgroundSubtractorGMG()
#

while True:
    ret,frame = cap.read()
    fgmask = fgbg.apply(frame)
    # knn
    fgmask = cv2.morphologyEx(fgmask,cv2.MORPH_OPEN,kernel)
    #
    cv2.imshow("frame",fgmask)

    k = cv2.waitKey(100) & 0xFF
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
