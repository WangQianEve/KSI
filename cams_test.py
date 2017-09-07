# USAGE
# python cams_test.py
# python cams_test.py --display 1

# import the necessary packages
from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils
import cv2
import numpy as np
import time
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--display", type=int, default=1,
	help="Whether or not frames should be displayed")
ap.add_argument("-o", "--output", type=int, default=0,
    help="Whether to write video files: -1 to png, 0 no output, 1 to avi")
args = vars(ap.parse_args())

def single_raw_test(w,h):
	# grab a pointer to the video stream and initialize the FPS counter
	print("[TEST1] sampling frames from webcam...")
	cap0 = cv2.VideoCapture(1)
	cap0.set(cv2.CAP_PROP_FRAME_WIDTH, w);
	cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, h);
	cap0.set(cv2.CAP_PROP_FPS, 200)
	
	(grabbed0, frame0) = cap0.read() # magic line
	count = 0
	fps = FPS().start()
	while True:
		count += 1
		(grabbed0, frame0) = cap0.read()
		if args["display"] > 0:
			cv2.imshow("Frame0", frame0)
			key = cv2.waitKey(1) & 0xFF
			if key == 27:
				break	
		fps.update()
		if args["output"]<0:
			cv2.imwrite("./fRecord/"+str(count)+".png",frame0)
	
	fps.stop()
	print("[TEST1] elasped time: {:.2f}".format(fps.elapsed()))
	print("[TEST1] approx. FPS: {:.2f}".format(fps.fps()))
	
	# do a bit of cleanup
	cap0.release()
	cv2.destroyAllWindows()
	return int(fps.fps())

def raw_test(w,h):
	# grab a pointer to the video stream and initialize the FPS counter
	print("[TEST1] sampling frames from webcam...")
	
	cap0 = cv2.VideoCapture(1)
	cap0.set(cv2.CAP_PROP_FRAME_WIDTH, w);
	cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, h);
	cap0.set(cv2.CAP_PROP_FPS, 200)
	cap1 = cv2.VideoCapture(2)
	cap1.set(cv2.CAP_PROP_FRAME_WIDTH, w);
	cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, h);
	cap1.set(cv2.CAP_PROP_FPS, 200)
	
	(grabbed0, prev_frame) = cap0.read()
	(grabbed0, prev_frame) = cap1.read()
	count = 0
	fps = FPS().start()
	# loop over some frames
	while True: #fps._numFrames < args["num_frames_raw"]:
		count += 1
		(grabbed0, frame0) = cap0.read()
		(grabbed1, frame1) = cap1.read()
		if args["display"] > 0:
			cv2.imshow("Frame1", frame1)
			cv2.imshow("Frame0", frame0)
			key = cv2.waitKey(1) & 0xFF
			if key == 27:
				break	
		# update the FPS counter
		fps.update()
		if args["output"]<0:
			cv2.imwrite("./fRecord/a"+str(count)+"_0.png",frame0)
			cv2.imwrite("./fRecord/a"+str(count)+"_1.png",frame1)
	
	# stop the timer and display FPS information
	fps.stop()
	print("[TEST1] elasped time: {:.2f}".format(fps.elapsed()))
	print("[TEST1] approx. FPS: {:.2f}".format(fps.fps()))
	
	# do a bit of cleanup
	cap0.release()
	cap1.release()
	cv2.destroyAllWindows()
	return int(fps.fps())

# created a *threaded *video stream, allow the camera senor to warmup,
# and start the FPS counter
def notBlack(image):
	arr = np.append(image,[0])
	sum = np.sum(arr)
	if sum == 0:
		return False 
	return True

def threaded_test():
	print("[TEST2] sampling THREADED frames from webcam...")
	vs0 = WebcamVideoStream(src=1).start()
	vs1 = WebcamVideoStream(src=2).start()
	fps = FPS().start()
	prev_frame = vs1.read()
	# loop over some frames...this time using the threaded stream
	while fps._numFrames < args["num_frames_thr"]:
		# grab the frame from the threaded video stream and resize it
		# to have a maximum width of 400 pixels
		frame0 = vs0.read()
		frame1 = vs1.read()
		diff = frame1-prev_frame
		prev_frame = frame1
		time.sleep(0.04)
		# check to see if the frame should be displayed to our screen
		if args["display"] > 0:
			cv2.imshow("Frame1", frame1)
			cv2.imshow("Frame0", frame0)
			key = cv2.waitKey(1) & 0xFF
	
		# update the FPS counter
		if notBlack(diff):
			fps.update()
	
	# stop the timer and display FPS information
	fps.stop()
	print("[TEST2] elasped time: {:.2f}".format(fps.elapsed()))
	print("[TEST2] approx. FPS: {:.2f}".format(fps.fps()))
	
	# do a bit of cleanup
	cv2.destroyAllWindows()
	vs0.stop()
	vs1.stop()
	return int(fps.fps())>>4<<4

if __name__ == '__main__':
	#threaded_test()
	raw_test(640,480)
	#single_raw_test(640,480)