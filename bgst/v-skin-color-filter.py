import numpy as np
import cv2
import argparse
# Notation explaination
### means code are used for debugging
# xxx means steps' title

def apply_hist_mask(frame, hist):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([hsv], [0,1], hist, [0,180,0,256], 1)
    #gause = cv2.GaussianBlur(dst, (5,5), 0)
    #median = cv2.medianBlur(dst,5);
    #dst = gause
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    #
    cv2.filter2D(dst, -1, disc, dst)
    ret, thresh = cv2.threshold(dst, 0, 255, 0)
    return thresh

def distance(start, end):
    if end[0] == -1 :
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

def addt(a,b):
    return (a[0]+b[0],a[1]+b[1])

def equal(a,b):
    if a[0]==b[0] and a[1]==b[1]: return True
    return False
    
def convex(pp,p,c):
    th = 60
    la = distance(p,pp)
    lb = distance(p,c)
    if la<th and lb<th:
        sm = True
    else:
        sm = False
    a = subt(p,pp)
    cos = angle(a,(1,0))
    sin = np.sqrt(1-cos*cos)
    if a[1]<0:
        sin = -1*sin
    b = subt(c,p)
#     bx = b[0]*cos + b[1]*sin
    by = -1*b[0]*sin+ b[1]*cos
    if by<0:
        return sm,False
    else:
        return sm,True
    
def angle(a,b):
    a = list(a)
    b = list(b)
    if abs(a[0])>64 or abs(a[1])>64:
        a[0] >>= 4
        a[1] >>= 4
    if abs(b[0])>64 or abs(b[1])>64:
        b[0] >>= 4
        b[1] >>= 4
    return (a[0]*b[0] + a[1]*b[1])/np.sqrt((a[0]*a[0] + a[1]*a[1])*(b[0]*b[0] + b[1]*b[1]) + 1e-10)

def large_regions(area_thresh,contours):
    cnt=[]
    for i in range(len(contours)):
        cntt=contours[i]
        area = cv2.contourArea(cntt)
        if area>area_thresh:
            cnt += cntt.tolist()
    return cnt

def largest(area_thresh,contours):
    max_area=area_thresh
    ci = -1
    for i in range(len(contours)):
            cnt=contours[i]
            area = cv2.contourArea(cnt)
            if(area>max_area):
                max_area=area
                ci=i
    if ci<0: cnt=[]
    else: cnt=contours[ci]
    return cnt

def findNearestP(p_approx, point,av,_index_a,centr):
    min_dist = 100
    p = (-1,-1)
    for i in range(p_approx.shape[0])[::-1]:
        dist = distance(p_approx[i-1][0],point)
        if dist>min_dist:
            continue
        if angle(subt(p_approx[i-1][0],centr),av)>_index_a:
            continue
        ca,cb = convex(p_approx[i][0],p_approx[i-1][0],p_approx[i-2][0])
        if cb:
            min_dist = dist
            p = p_approx[i-1][0] 
    return tuple(p)

def findNearestT(p_approx, point, av, _index_a, centr):
    min_dist = 160
    p = (-1,-1)
    for i in range(p_approx.shape[0])[::-1]:
        dist = distance(p_approx[i-1][0],point)
        if dist>min_dist:
            continue
        if angle(subt(p_approx[i-1][0],centr),av)<_index_a:
            continue
        ca,cb = convex(p_approx[i][0],p_approx[i-1][0],p_approx[i-2][0])
        if cb:
            min_dist = dist
            p = p_approx[i-1][0] 
    return tuple(p)

def square(frame):
    global roihist_n
    io = apply_hist_mask(frame, roihist_n)
    _, contours, hierarchy = cv2.findContours(io,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnt = largest(100,contours)
    if len(cnt)<3:
        return [-1,-1]
    x,y,w,h = cv2.boundingRect(cnt)
    return [x+w-5,y+5]

def draw_contours(thresh,img):
    _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # find the larg region
    cnt = large_regions(300,contours)
    p_cnt = largest(1000,contours)
    if len(p_cnt)==0: return img
    # convex hull
    cnt = np.asarray(cnt)
    hull = cv2.convexHull(np.asarray(cnt),clockwise=False)
    # poly
    p_cnt = np.asarray(p_cnt)
    epsilon = 0.005*cv2.arcLength(p_cnt,True)
    p_approx = cv2.approxPolyDP(p_cnt,epsilon,True)
    # calculate center
    moments = cv2.moments(hull)
    if moments['m00']!=0:
        cx = int(moments['m10']/moments['m00']) # cx = M10/M00
        cy = int(moments['m01']/moments['m00']) # cy = M01/M00
    centr=(cx,cy)
### 
    if args["draw"] > 0:
        cv2.drawContours(img,[cnt],0,_c_pink,1)
        cv2.drawContours(img,[p_approx],0,_c_green,1)
#         cv2.drawContours(img,[hull],0,_c_pink,2)
        cv2.circle(img,centr,5,_c_pink,-1)
    if hull is not None and len(hull > 3) and len(cnt) > 3:
        hull = np.append(hull,[hull[0]],0)
        ax = (-1,-1)
# find leftmost bottom
        _bottom_a = 0.85
        _bottom_x = 20
        _bottom_l = 60
        last_i = -1
        for i in range(hull.shape[0]-1)[::-1]:
            end = tuple(hull[i][0])
            start = tuple(hull[i+1][0])
            if args["draw"] > 0:
                cv2.circle(img,end,3,_c_blue,-1)
            if start[0]>_bottom_x or end[0]>_bottom_x:
                continue
            length = distance(start,end)
            if length<_bottom_l:
                continue
            last_i = i
            break
        if last_i <0:
            return img
        bc = distance(start,centr)
        prev_start = start
        if args["draw"] > 0:
            cv2.circle(img,prev_start,5,_c_yellow,-1)
# find rightmost line
        _right_l = 40
        _right_dis = 30
        sym = (-1,-1)
        for i in range(last_i)[::-1]:
            end = tuple(hull[i][0])
            start = tuple(hull[i+1][0])
            if end[0]-start[0]<_right_dis:
                continue
            length = distance(start,end)
            if length > _right_l:
                sym = calSim(bc,centr,start,end)
                if args["draw"] > 0:
                    cv2.circle(img,sym,5,_c_yellow,-1)
                ax = subt(sym,prev_start)
                av = addt(subt(prev_start,centr), subt(sym,centr))
                break
        if sym[0] == -1:
            return img
        if args["draw"] > 0:
            cv2.line(img,centr,addt(centr,av),_c_pink,2)
# find fingers
        _index_l = 10 # may delete
        _index_a = -0.75
        _thumb_l = 50
        _thumb_a = 0
        p_thumb = (-1,-1)
        p_index = (-1,-1)
        for i in range(last_i+1,hull.shape[0]-1):
            end = tuple(hull[i][0])
            start = tuple(hull[i+1][0])
            length = distance(start,end)
# find thumb
            if length>_thumb_l:
                if angle(subt(end,centr),av) < _thumb_a:
                    thumb = end
                    i_thumb = i
                    p_thumb = findNearestT(p_approx,thumb,av,_index_a,centr)
                    if args["draw"] > 0:
                        cv2.circle(img,thumb,7,_c_blue,-1)
                        if p_thumb[0]>0:
                            cv2.circle(img,p_thumb,5,_c_pink,-1)
                    _thumb_l = 640
# find index                    
            if length>_index_l:
                if start[0] < 180:
                    continue
                if end[0] < 180:
                    continue
                c_angle = angle(subt(end,centr),av)
                if c_angle<_index_a:
                    index = end
                    i_index = i
                    p_index = findNearestP(p_approx,index,av,_index_a,centr)
                    if args["draw"] > 0:
                        cv2.circle(img,end,7,_c_yellow,-1)
                        if p_index[0]>0:
                            cv2.circle(img,p_index,5,_c_light_blue,-1)
                    break
                c_angle = angle(subt(start,centr),av)
                if c_angle<_index_a:
                    index = start
                    i_index = i+1
                    p_index = findNearestP(p_approx,start,av,_index_a,centr)
                    if args["draw"] > 0:
                        cv2.circle(img,start,7,_c_yellow,-1)
                        if p_index[0]>0:
                            cv2.circle(img,p_index,5,_c_light_blue,-1)
                    break
# check inside
        if p_index[0]>0 and p_thumb[0]>0 and not equal(p_index,p_thumb):
            flag = False
            indexl = []
            prevprev = -1
            prev = -1
            enter = False
            after_concave=0
            for i in np.append(p_approx[::-1],p_approx[::-1],axis = 0):
                i=i[0]
                if equal(i,p_thumb):
                    flag = True
                    count = 1
                    enter = True
                elif equal(i,p_index):
                    flag = False
                    if enter:
                        break
                if flag:
                    if count<0:
                        small,conv = convex(prevprev,prev,i)
                        if conv:
                            if after_concave==1 and not small:
                                indexl.append(prev)
                        else:
                            if not small:
                                if len(indexl)==0: after_concave = 1
                                else: after_concave += 1
                    else:
                        count -= 1
                    prevprev=prev
                    prev=i   
            if len(indexl)>0:
                global maincount
                print "red "+str(maincount)
                print indexl
                if len(indexl) > 1:
                    print "mul"
                    indexl = np.array(indexl)
                    p_index = (int(np.mean(indexl[:,0])), int(np.mean(indexl[:,1])))
                else:
                    p_index = tuple(indexl[0])
                if args["draw"] > 0:
                    cv2.circle(img,p_index,5,_c_red,-1)
# stablizer
        if p_index[0]>=0:
            x1 = p_index[0]-40
            if x1<0: x1 = 0
            x2 = p_index[0]+40
            if x2>img.shape[1]: x2 = img.shape[1]
            y1 = p_index[1]-40
            if y1<0: y1 = 0
            y2 = p_index[1]+40
            if y2>img.shape[0]: y2 = img.shape[0]
            n_index = square(img[y1:y2,x1:x2])
            n_index[0] += x1
            n_index[1] += y1
            cv2.circle(img,tuple(n_index),5,_c_white,-1)
    return img

def main():
    global maincount, roihist_n
    hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
    hsv_n = cv2.cvtColor(roi_n,cv2.COLOR_BGR2HSV)
    roihist = cv2.calcHist([hsv],[0, 1], None, [180, 256], [0, 180, 0, 256] )
    roihist_n = cv2.calcHist([hsv_n],[0, 1], None, [180, 256], [0, 180, 0, 256] )
    cv2.normalize(roihist,roihist,0,255,cv2.NORM_MINMAX)
    cv2.normalize(roihist_n,roihist_n,0,255,cv2.NORM_MINMAX)
    maincount = 0
    while True:
        maincount+=1
        if maincount == 208:
            bp=1
        ret, frame = cap.read()
        if not ret:
            return
        frame = frame[:,crop[0]:crop[1]]
        out = apply_hist_mask(frame,roihist)
        rout = out.copy()
        img = draw_contours(out,frame)
        if args["display"] > 0:
            cv2.imshow('thr',rout)
            cv2.imshow('org',img)
            time = 1
            k = cv2.waitKey(time)
            if k == 32:
                cv2.waitKey(5000)
            if k == ord('q'):
                break    
        if args['output'] < 0:
            cv2.imwrite("./observe-1/"+str(maincount)+".png",img)
        if args['output']>0:
            outCv.write(img)
            outTh.write(cv2.merge((rout,rout,rout)))

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=int, default=1,
    help="Whether to write video files")
ap.add_argument("-r", "--draw", type=int, default=1,
    help="Whether to draw")
ap.add_argument("-d", "--display", type=int, default=1,
    help="Whether or not frames should be displayed")
args = vars(ap.parse_args())
# colors
_c_blue =       (255,64,64)
_c_light_blue = (255,160,64)
_c_red =        (32,32,255)
_c_pink =       (128,128,255)
_c_green =      (64,255,0)
_c_yellow =     (0,196,255)
_c_white =      (255,255,255)
# 
crop = (256,640)
cap = cv2.VideoCapture('./TestVideo/video0.avi')
roi = cv2.imread('./TestVideo/video0.png')
roi_n = cv2.imread('./TestVideo/nail0.png')
# video out
if args['output']>0:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    outTh = cv2.VideoWriter('./TestResultVideo/SCF-th.avi', fourcc,12,(384,480))
    outCv = cv2.VideoWriter('./TestResultVideo/SCF-cv.avi', fourcc,12,(384,480))
# index approx
main()
cap.release()
cv2.destroyAllWindows()
