'''
Created on Aug 8, 2017

@author: qian
'''
from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils
import cv2
import numpy as np

a=[]

def skin_find(img,title):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(9,9),0)
#    cv2.imshow('blur-gauss',blurg)
#    blurb = cv2.bilateralFilter(gray,9,75,75)
#    cv2.imshow('blur-bilate',blurb)
#    blur = cv2.medianBlur(gray,7)
#    cv2.imshow('blur-median',blur)
    ret,thresh1 = cv2.threshold(blur,80,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
  
    _, contours, hierarchy = cv2.findContours(thresh1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    drawing = np.zeros(img.shape,np.uint8)

    max_area=0
   
    for i in range(len(contours)):
            cnt=contours[i]
            area = cv2.contourArea(cnt)
            if(area>max_area):
                max_area=area
                ci=i
    cnt=contours[ci]
    hull = cv2.convexHull(cnt)
    prev_hull = cv2.convexHull(cnt)
    prev_cnt = cnt
    moments = cv2.moments(cnt)
    if moments['m00']!=0:
                cx = int(moments['m10']/moments['m00']) # cx = M10/M00
                cy = int(moments['m01']/moments['m00']) # cy = M01/M00
              
    centr=(cx,cy)
    if args["display"] > 0:
        cv2.circle(img,centr,5,[0,0,255],2)       
        cv2.drawContours(drawing,[cnt],0,(0,255,0),2) 
        cv2.drawContours(drawing,[hull],0,(255,0,255),2) 
          
    cnt = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
    hull = cv2.convexHull(cnt,returnPoints = False)

    defects = cv2.convexityDefects(cnt,hull)
    mind=0
    maxd=0
    if defects is None:
        return
    for i in range(defects.shape[0]):
         s,e,f,d = defects[i,0]
         start = tuple(cnt[s][0])
         end = tuple(cnt[e][0])
         far = tuple(cnt[f][0])
         dist = cv2.pointPolygonTest(cnt,centr,True)
    if args["display"] > 0:
         cv2.line(img,start,end,[0,255,0],2)
         cv2.circle(img,far,5,[0,0,255],-1)
    if args["display"] > 0:
        cv2.imshow('out-'+title,drawing)
        cv2.imshow('in-'+title,img)
#        cv2.imshow('bg-'+title,thresh1)
     
# construct the argument parse and parse the arguments

def main():
    global a
    fps = FPS().start()
    # loop over some frames...this time using the threaded stream
    while True:
        ret, frame = cap.read()
        if not ret:
            return
        frame = frame[:,crop[0]:crop[1]]
        skin_find(frame,"frame")
        if cv2.waitKey(100) & 0xFF == ord('q'):
            return
        # check to see if the frame should be displayed to our screen
    
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=1000,
    help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=1,
    help="Whether or not frames should be displayed")
args = vars(ap.parse_args())

crop = (256,640)
cap = cv2.VideoCapture('./TestVideo/moving0.avi')
# roi = cv2.imread('./TestVideo/moving1.JPG')
# video out
fourcc = cv2.VideoWriter_fourcc(*'XVID')
outTh = cv2.VideoWriter('./TestResultVideo/BF-th.avi', fourcc,24,(384,480))
outCv = cv2.VideoWriter('./TestResultVideo/BF-cv.avi', fourcc,24,(384,480))
main()
cap.release()
cv2.destroyAllWindows()
