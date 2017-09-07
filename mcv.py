'''
my cv, basic functions about 2-d points
@author: qian
'''
import cv2
import numpy as np
import collections
def clean(frame):
    frame = np.append(frame,[[0]])
    ave = np.mean(frame)
    std = np.std(frame)
    if ave<0.01 and std<2:
        return True
    return False

def broken(frame,th):
    _, contours, hierarchy = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnt = largeN(th,contours)
    if cnt>=2:
        return True
    return False
    
def area(frame):
    frame = np.append(frame,[[0]])
    valid = frame[frame>0]
    return len(valid)
    
def diff(frame1,frame2):
    frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    diff = frame1-frame2
    std = np.std(diff)
    if std>100:
        return False
    return True

def aveBrightness(frame,th=60):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #
    valid = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY)[1]
    cv2.imshow("hand",valid)
    cv2.waitKey(1)
    brightness=collections.deque()
    for row in gray:
        for col in row:
            if col>th:
                brightness.append(col)
    return np.mean(brightness)

def largeN(area_thresh,contours):
    c = 0
    for i in range(len(contours)):
            cnt=contours[i]
            area = cv2.contourArea(cnt)
            if(area>area_thresh):
                c+=1
    return c

def largest(area_thresh,contours):
    '''
    Find the biggest contour from a group of contours with a minimal area limit.
    params:
        area_thresh : minimal area threshold
        contours: all the candidates
    output: array of points that forms the contour or a empty list
    '''
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

def distance(start, end):
    '''
    return the distance of two 2d points
    params: 
        start end : tuples of 2
    output: float
    '''
    return np.sqrt((start[0]-end[0])**2+(start[1]-end[1])**2)

def subt(a,b):
    '''
    return difference of two 2-d points, a and b
    a,b: tuples
    output: tuple of 2, datatype the same as input
    '''
    return (a[0]-b[0],a[1]-b[1])

def addt(a,b):
    '''
    return addition of two 2-d points, a and b
    a,b: tuples
    output: tuple of 2
    '''
    return (a[0]+b[0],a[1]+b[1])

def equal(a,b):
    '''
    return whether a equals b
    a,b: tuples of 2
    output: bool
    '''
    if a[0]==b[0] and a[1]==b[1]: return True
    return False

def zero(a):
    '''
    return whether a equals (0,0)
    a: tuples of 2
    output: bool
    '''
    if a[0]==0 and a[1]==0: return True
    return False
    
def convex(pp,p,c,th=60):
    '''
    tell if a point is a convex or a concave, and whether it is a big one. Neither convex or concave is considered convex.
    input:
        pp,p,c: 3 clockwise sequential points ,the 2nd one is the test target
        th: optional, if both edges are smaller than th, it is considered small
    output:
        tuple(bool isSmall,bool isConvex)
    '''
    la = distance(p,pp)
    lb = distance(p,c)
    if la<th and lb<th:
        sm = True
    else:
        sm = False
    a = subt(p,pp)
    b = subt(c,p)
    if zero(a) or zero(b):
        raise NameError("convex test must be 3 different points")
    cos = angle(a,(1,0))
    sin = np.sqrt(1-cos*cos)
    if a[1]<0:
        sin = -1*sin
#     bx = b[0]*cos + b[1]*sin
    by = -1*b[0]*sin+ b[1]*cos
    if by<0:
        return sm,False
    else:
        return sm,True

def angle(a,b):
    '''
    return the cosine value of the angle formed by vector a and b
    a,b: tuples of 2, cannot be zero
    output: float
    '''
    if zero(a):
        raise NameError("cannot calculate angle of (0,0) with others")
    if zero(b):
        raise NameError("cannot calculate angle of others with (0,0) ")
    a = list(a)
    b = list(b)
    return (a[0]*b[0] + a[1]*b[1])/np.sqrt((a[0]**2 + a[1]**2)*(b[0]**2 + b[1]**2))

def calSim(d,centr,start,end):
    '''
    find a point on a line that has certain distance from a point. If not, find the nearest point.
    Args:
        d: the distance
        centr: the point
        start, end: two endpoint of the line.
    Return: 
        (int,int) the point's coordinate (tuple of 2)
    '''
    c = int(distance(start, end)/10)
    if c==0: return start
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

def ptoint(p):
    return (int(p[0]),int(p[1]))

def getRec(pr_index,cropx,cropy,shape):
    '''
    crop a square area that contains a point pr_index
    input:
        pr_index: int, the point
        crop: int, the half length of side
        shape: tuple of 2, the original image's shape
    output:
        tuple of 4
    '''
    rec=[0,0,0,0]
    rec[0] = pr_index[0]-cropx
    if rec[0]<0:rec[0] = 0
    rec[1] = pr_index[0]+cropx
    if rec[1]>shape[1]: rec[1] = shape[1]
    rec[2] = pr_index[1]-cropy
    if rec[2]<0: rec[2] = 0
    rec[3] = pr_index[1]+cropy
    if rec[3]>shape[0]: rec[3] = shape[0]
    return rec
