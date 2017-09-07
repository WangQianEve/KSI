'''
Created on Aug 8, 2017

@author: qian
'''
# USAGE
# python record.py
# python record.py --display 1 --output 1

# import the necessary packages
from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import imutils
import cv2
import argparse
import cams_test
import numpy as np
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--display", type=int, default=1,
    help="Whether or not frames should be displayed")
ap.add_argument("-o", "--output", type=int, default=1,
    help="Whether to write video files: -1 to png, 0 no output, 1 to avi")
args = vars(ap.parse_args())
def raw_record(w,h):
    speed = 200
    print("[INFO] recording with fps "+str(speed))
    vs0 = cv2.VideoCapture(1)
    vs0.set(cv2.CAP_PROP_FRAME_WIDTH, w);
    vs0.set(cv2.CAP_PROP_FRAME_HEIGHT, h);
    vs0.set(cv2.CAP_PROP_FPS, 200)
    vs1 = cv2.VideoCapture(2)
    vs1.set(cv2.CAP_PROP_FRAME_WIDTH, w);
    vs1.set(cv2.CAP_PROP_FRAME_HEIGHT, h);
    vs1.set(cv2.CAP_PROP_FPS, 200)
    
    (grabbed0, prev_frame) = vs0.read()
    (grabbed0, prev_frame) = vs1.read()
    if args['output'] > 0:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out0 = cv2.VideoWriter('ksivideo0.avi', fourcc,speed,(w,h))
        out1 = cv2.VideoWriter('ksivideo1.avi', fourcc,speed,(w,h))
#         out0 = cv2.VideoWriter('./TestData/video/nback0.avi', fourcc,speed,(w,h))
#         out1 = cv2.VideoWriter('./TestData/video/nback1.avi', fourcc,speed,(w,h))
    # loop over some frames...this time using the threaded stream
    fps = FPS().start()
    recording = False
    while True:
        (grabbed0, frame0) = vs0.read()
        (grabbed1, frame1) = vs1.read()
        if args["display"] > 0:
            cv2.imshow("Frame1", frame1)
            cv2.imshow("Frame0", frame0)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break    
            if key ==32:
                if recording:
                    recording = False
                    print ("end")
                else:
                    recording=True
                    print ("recording")
        if args['output'] > 0 and recording:
            out0.write(frame0)
            out1.write(frame1)
        fps.update()
    
    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    
    # do a bit of cleanup
    if args['output'] > 0:
        out0.release()
        out1.release()
    vs0.release()
    vs1.release()
    cv2.destroyAllWindows()

def threaded_record():
    cams_test.raw_test()
    speed = cams_test.threaded_test()
    print("[INFO] recording with fps "+str(speed))
    # created a *threaded *video stream, allow the camera senor to warmup,
    # and start the FPS counter
    vs0 = WebcamVideoStream(src=1).start()
    vs1 = WebcamVideoStream(src=2).start()
    if args['output'] > 0:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out0 = cv2.VideoWriter('./TestVideo/video0.avi', fourcc,speed,(640,480))
        out1 = cv2.VideoWriter('./TestVideo/video1.avi', fourcc,speed,(640,480))
    # loop over some frames...this time using the threaded stream
    fps = FPS().start()
    while True:
        frame0 = vs0.read()
        frame1 = vs1.read()
        if args['output'] > 0:
            out0.write(frame0)
            out1.write(frame1)
        if args['display'] > 0:
            cv2.imshow("Frame0", frame0)
            cv2.imshow("Frame1", frame1)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
        fps.update()
    
    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    
    # do a bit of cleanup
    if args['output'] > 0:
        out0.release()
        out1.release()
    vs0.stop()
    vs1.stop()
    cv2.destroyAllWindows()
    
def notBlack(image):
    arr = np.append(image,[0])
    sum = np.sum(arr)
    if sum == 0:
        return False 
    return True

def threaded_check():
    #cams_test.raw_test()
    #cams_test.threaded_test()
    print("[INFO] saving image...")
    # created a *threaded *video stream, allow the camera senor to warmup,
    # and start the FPS counter
    vs1 = WebcamVideoStream(src=1).start()
    # loop over some frames...this time using the threaded stream
    count = 0
    prev_frame = vs1.read()
    fps = FPS().start()
    while count<1000:
        count += 1
        frame1 = vs1.read()
#         gray = cv2.cvtColor((frame1-prev_frame), cv2.COLOR_BGR2GRAY)
#         ret, diff = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
        diff = frame1-prev_frame
#         if args['output'] < 0:
#             cv2.imwrite("./fRecord/"+str(count)+".png",frame1)
#             cv2.imwrite("./tRecord/"+str(count)+"_d.png",frame1-prev_frame)
        prev_frame = frame1
        if args['display'] > 0:
            cv2.imshow("Frame1", frame1)
#            cv2.imshow("Diff", diff)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
        if notBlack(diff):
            fps.update()
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    vs1.stop()
    cv2.destroyAllWindows()
    
def mix_record():
    #cams_test.raw_test()
    #cams_test.threaded_test()
    print("[INFO] saving image...")
    # created a *threaded *video stream, allow the camera senor to warmup,
    # and start the FPS counter
    vs0 = cv2.VideoCapture(1)
    vs1 = WebcamVideoStream(src=2).start()
    # loop over some frames...this time using the threaded stream
    count = 0
    while True:
        count += 1
        ret, frame0 = vs0.read()
        frame1 = vs1.read()
        if args['output'] < 0:
            cv2.imwrite("./mixRecord/"+str(count)+"_r.png",frame0)
            cv2.imwrite("./mixRecord/"+str(count)+"_t.png",frame1)
        if args['display'] > 0:
            cv2.imshow("Frame0", frame0)
            cv2.imshow("Frame1", frame1)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
    vs0.release()
    vs1.stop()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    raw_record(320,240)
    #mix_record()
    #threaded_check()
    #threaded_record()