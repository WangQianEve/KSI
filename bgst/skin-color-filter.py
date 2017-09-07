import numpy as np
import cv2
import argparse
from imutils.video import FPS
from imutils.video import WebcamVideoStream

def apply_hist_mask(frame, hist):
    global fps
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([hsv], [0,1], hist, [0,180,0,256], 1)
    #gause = cv2.GaussianBlur(dst, (5,5), 0)
    #median = cv2.medianBlur(dst,5);
    #dst = gause
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    cv2.filter2D(dst, -1, disc, dst)
    ret, thresh = cv2.threshold(dst, 10, 255, 0)
    return thresh

def distance(start, end):
    if end ==0:
        return 0
    return np.sqrt((start[0]-end[0])**2+(start[1]-end[1])**2)

def calSim(d,centr,start,end):
    c = int(distance(start, end)/10)
    dx = (end[0] - start[0])/(c+0.0)
    dy = (end[1] - start[1])/(c+0.0)
    x = start[0]
    y = start[1]
    ax = x
    ay = y
    delta = d
    t_delta = 5
    for i in range(c):
        dis = distance((x,y),centr)
        abdis = abs( dis-d )
        if abdis < delta:
            if abdis < t_delta:
                return (int(x),int(y))
            delta = abdis
            ax = x
            ay = y
        x+=dx
        y+=dy
    return (int(ax),int(ay))

def subt(a,b):
    return (a[0]-b[0],a[1]-b[1])

def angle(a,b):
    return (a[0]*b[0] + a[1]*b[1])/np.sqrt((a[0]*a[0] + a[1]*a[1])*(b[0]*b[0] + b[1]*b[1]) + 1e-10)

def draw_contours(thresh,img):
    global pre, fps
    _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # find the larg region
    cnt=[]
    area_thresh = 300
    for i in range(len(contours)):
        cntt=contours[i]
        area = cv2.contourArea(cntt)
        if area>area_thresh:
            cnt += cntt.tolist()
    if len(cnt)==0: return img
    # convex hull
    cnt = np.asarray(cnt)
    hull = cv2.convexHull(np.asarray(cnt))#,clockwise=True)
    # calculate center
    moments = cv2.moments(hull)
    if moments['m00']!=0:
        cx = int(moments['m10']/moments['m00']) # cx = M10/M00
        cy = int(moments['m01']/moments['m00']) # cy = M01/M00
    centr=(cx,cy)
    # drawing
    if args["display"] > 0:
        cv2.drawContours(img,[cnt],0,(0,255,0),2)
        cv2.drawContours(img,[hull],0,(100,0,100),2)
        cv2.circle(img,centr,5,[100,0,100],-1)
    
    # locating index
    hull = cv2.convexHull(cnt, returnPoints=False, clockwise = False)
    if hull is not None and len(hull > 3) and len(cnt) > 3:
        defects = cv2.convexityDefects(cnt,hull)
        if defects is not None:
            # check clockwise
            if cnt[defects[0,0][0]][0][1]<cnt[defects[0,0][1]][0][1]:
                defects = defects[::-1]
                for i in range(defects.shape[0]):
                    t = defects[i,0][0]
                    defects[i,0][0] = defects[i,0][1]
                    defects[i,0][1] = t
                    
            ax = 0
            # find leftmost bottom
            _bottom_x = 20
            _bottom_l = 60
            last_i = -1
            for i in range(defects.shape[0]):
                s,e,f,d = defects[i,0]
                start = tuple(cnt[s][0])
                end = tuple(cnt[e][0])
                if start[0]>_bottom_x or end[0]>_bottom_x:
                    continue
                # far = tuple(cnt[f][0])
                length = distance(start,end)
                if length<_bottom_l:
                    continue
                last_i = i
                break
            if last_i <0:
                return img
            bc = distance(start,centr)
            prev_start = start
            cv2.circle(img,prev_start,5,[0,255,255],-1)
            # find rightmost line
            _right_l = 40
            _right_dis = 30
            for i in range(last_i+1,defects.shape[0]):
                s,e,f,d = defects[i,0]
                start = tuple(cnt[s][0])
                end = tuple(cnt[e][0])
                # Debug
                if args["display"] > 0:
                     cv2.line(img,start,end,[0,255,0],2)
                     cv2.circle(img,end,3,[255,0,0],-1)
                #/
                if end[0]-start[0]<_right_dis:
                    continue
                length = distance(start,end)
                if length > _right_l:
                    cv2.line(img,start,end,[0,0,255],2)
                    sym = calSim(bc,centr,start,end)
                    cv2.circle(img,sym,5,[0,255,255],-1)
                    ax = subt(sym,prev_start)
                    break
            # find index
            _index_l = 10 # may delete
            _index_a = -0.6
            _index_ah = -0.2
            for i in range(last_i)[::-1]:
                s,e,f,d = defects[i,0]
                start = tuple(cnt[s][0])
                end = tuple(cnt[e][0])
                length = distance(start,end)
                # Debug
                if args["display"] > 0:
                     cv2.line(img,start,end,[100,0,100],2)
                #/
                if length>_index_l:
                    if start[0] < 180:
                        continue
                    c_angle = angle(subt(end,centr),ax)
                    if c_angle>_index_a and c_angle<_index_ah:
                        if end[0] > 180:
                            cv2.circle(img,end,5,[0,200,255],-1)
                            # we can add this when fps is higher
#                             print distance(start,pre)
#                             if distance(start,pre)>30:
#                                 cv2.waitKey(5000)
#                             pre = start
                            break
                    c_angle = angle(subt(start,centr),ax)
                    if c_angle>_index_a and c_angle<_index_ah:
                        cv2.circle(img,start,5,[0,200,255],-1)
                        break
    return img

def main():
    global fps
    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    roihist = cv2.calcHist([hsv],[0, 1], None, [180, 256], [0, 180, 0, 256] )
    cv2.normalize(roihist,roihist,0,255,cv2.NORM_MINMAX)

    hsv1 = cv2.cvtColor(roi1,cv2.COLOR_BGR2HSV)
    roihist1 = cv2.calcHist([hsv1],[0, 1], None, [180, 256], [0, 180, 0, 256] )
    cv2.normalize(roihist1,roihist1,0,255,cv2.NORM_MINMAX)

    fps = FPS().start()
    while True:
        frame = cap.read()
        frame = frame[:,crop[0]:crop[1]]
        out = apply_hist_mask(frame,roihist)
        if args["display"] > 0:
            cv2.imshow('out',out)
        org = draw_contours(out,frame)
#         frame1 = cap1.read()
#         frame1 = frame1[:,crop1[0]:crop1[1]]
#         out1 = apply_hist_mask(frame1,roihist1)
#         org1 = draw_contours(out1,frame1)
        fps.update()
        if args["display"] > 0:
            cv2.imshow('org',org)
#             cv2.imshow('out1',out1)
#             cv2.imshow('org1',org1)
            k = cv2.waitKey(1)
            if k == 32:
                fps.stop()
                print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
                print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
                fps = FPS().start()
            elif k == 27:
                break
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--display", type=int, default=1,
    help="Whether or not frames should be displayed")
args = vars(ap.parse_args())
# test cam
#test_cam()
def test_cam():
    cap0 = cv2.VideoCapture(0)
    cap0.set(cv2.CAP_PROP_FPS, 60)
    cap1 = cv2.VideoCapture(1)
    cap1.set(cv2.CAP_PROP_FPS, 60)
    fps = FPS().start()
     
    # loop over some frames
    while fps._numFrames < 500:
        # grab the frame from the stream and resize it to have a maximum
        # width of 400 pixels
        (grabbed0, frame0) = cap0.read()
        (grabbed1, frame1) = cap1.read()
     
        # check to see if the frame should be displayed to our screen
        if args["display"] > 0:
    #        cv2.imshow("Frame1", frame1)
            cv2.imshow("Frame0", frame0)
            key = cv2.waitKey(1) & 0xFF
     
        # update the FPS counter
        fps.update()
     
    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
     
    # do a bit of cleanup
    cap0.release()
    cap1.release()
# #
pre = 0
crop = (256,640)
cap = WebcamVideoStream(src=1).start()
roi = cv2.imread('./TestVideo/sample_low_crop.jpg')

crop1 = (0,384)
cap1 = WebcamVideoStream(src=0).start()
roi1 = cv2.imread('./TestVideo/sample_high_crop.jpg')

main()

cap.stop()
cv2.destroyAllWindows()
