# -*- coding: utf-8 -*-
from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils
import cv2
import numpy as np
from scipy.spatial import ConvexHull
# version config
cv2.ocl.setUseOpenCL(False)

# mog2
fgbg = cv2.createBackgroundSubtractorMOG2()
#fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
# created a *threaded *video stream, allow the camera senor to warmup,
# and start the FPS counter
vs = WebcamVideoStream(src=0).start()
fps = FPS().start()

while True:
	frame = vs.read()
	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	blurb = cv2.bilateralFilter(gray,9,75,75)
	#frame = imutils.resize(frame, width=400)
	#if args["display"] > 0:
	fgmask = fgbg.apply(blurb)
	cv2.imshow("Frame",fgmask)
	key = cv2.waitKey(1) & 0xFF
	if key == 27:
	    break
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
