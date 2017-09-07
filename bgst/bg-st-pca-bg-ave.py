'''
Created on Aug 2, 2017
1. scan points: outliers
    remove? don't know how
2. use new contours
    max mean
    approax, then max
    box
@author: qian
'''
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import numpy as np
import cv2
import scipy
import argparse

import moviepy.editor as mpe
# from IPython.display import display
from glob import glob
import sys, os
import matplotlib.pyplot as plt
plt.imshow(img)
plt.show()
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=1000,
    help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
    help="Whether or not frames should be displayed")
args = vars(ap.parse_args())

vs0 = WebcamVideoStream(src=0).start()
vs1 = WebcamVideoStream(src=1).start()
# read in pre-calculated low_rank
low_rank_mean0 = np.load("low_rank_bg-test-k-left.npy")
low_rank_mean1 = np.load("low_rank_bg-test-k-right.npy")
dims = (480,640)
low_rank_matrix0 = np.reshape(low_rank_mean0, dims)
low_rank_matrix1 = np.reshape(low_rank_mean1, dims)

count = args['num_frames']
fps = FPS().start()
while True:
    count -=1
    frame0 = vs0.read()
    frame1 = vs1.read()
    frame0 = cv2.cvtColor(frame0,cv2.COLOR_BGR2GRAY)
    frame1 = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
    frame00 = abs(frame0-low_rank_matrix0).astype(np.uint8)
    frame10 = abs(frame1-low_rank_matrix1).astype(np.uint8)
    ret,thresh0 = cv2.threshold(frame00,100,255,cv2.THRESH_BINARY)#+cv2.THRESH_OTSU)
    ret,thresh1 = cv2.threshold(frame10,100,255,cv2.THRESH_BINARY)#+cv2.THRESH_OTSU)
    key = cv2.waitKey(1) & 0xFF
    fps.update()
    if args["display"] > 0:
        cv2.imshow("Frame1", thresh0)
        cv2.imshow("Frame0", thresh1)
        cv2.imshow("Frame10", frame0)
        cv2.imshow("Frame00", frame1)
        if key == 27:
            break
        if key == 32:
            fps.stop()
            print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
            fps = FPS().start()
    else:
        if count<0:
            break

fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
fps = FPS().start()

# do a bit of cleanup
cv2.destroyAllWindows()
vs0.stop()
vs1.stop()
