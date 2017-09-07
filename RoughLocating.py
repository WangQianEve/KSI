'''
Created on Aug 15, 2017

@author: qian
'''
import numpy as np
import cv2
import colors
import mcv
from mcv import equal
from timer import Timer
def findPalmDir(hull,_bottom_l,_left_l, _bottom_x,_right_l,_right_dis,centr):
    '''
    This function find the palm direction and return the endpoints of wrist line 
    and the negative of palm direction. If left/right edge is not found, use the endpoint.
    If leftmost/rightmost was not found, sym and plam direction will be (0,0).
    The algorithm is described below:
        1. find the leftmost point of wrist
        2. find the rightmost point of wrist
        3. determine which side of hand should be checked and find the symmetry point
        4. use left/rightmost point, symmetry point, and centr of palm to calculate the direction of palm
    Args:
        hull: array of points, convex hull of the hand
        _bottom_l: minimal length limit of wrist
        _left_l: minimal length limit of left side of hand
        _bottom_x: maximal distance limit of wrist to edge of image
        _right_l: minimal length limit of right side of hand
        _right_dis: help find right side, minimal range of distance
        _centr: tuple of 2, center of the hand
    Return: tuple of 4
        the number of leftmost point (for further usage)
        left/rightmost point
        symmetry point
        the direction from palm to arm
    '''
    leftmost = (0,0)
    rightmost = (0,0)
    sym = (0,0)
    av = (0,0)
    last_i = -1
    lstart = (0,0)
    # leftmost
    for i in range(hull.shape[0]-1)[::-1]:
        end = tuple(hull[i][0])
        start = tuple(hull[i+1][0])
        length = mcv.distance(start,end)
        if length<_left_l:
            continue
        if start[0]<_bottom_x and end[0]<_bottom_x:
            last_i = i+1
            leftmost = start
            lc = mcv.distance(leftmost,centr)
            break
        else:
            lstart = end
            lend = start            
    if mcv.zero(lstart):
        lstart = leftmost
        lend = leftmost
    # rightmost
    last = -1
    for i in range(last_i)[::-1]:
        end = tuple(hull[i][0])
        start = tuple(hull[i+1][0])
        if start[0]>_bottom_x or end[0]>_bottom_x:
            rightmost = start
            rc = mcv.distance(centr,rightmost)
            if rc<lc:
                sym = mcv.calSim(rc,centr,lstart,lend)
                av = mcv.addt(mcv.subt(rightmost,centr), mcv.subt(sym,centr))
                return last_i,sym,rightmost,av
            else:
                last = i+1
                break
    # rightline
    for i in range(last)[::-1]:
        end = tuple(hull[i][0])
        start = tuple(hull[i+1][0])
        length = mcv.distance(start,end)
        if length > _right_l:
            sym = mcv.calSim(lc,centr,start,end)
            av = mcv.addt(mcv.subt(leftmost,centr), mcv.subt(sym,centr))
            break
    # cannot find rightline
    if mcv.zero(sym) and not mcv.zero(rightmost):
        sym = rightmost
        av = mcv.addt(mcv.subt(leftmost,centr), mcv.subt(sym,centr))

    return last_i,leftmost,sym,av

def findNearest(p_approx, point,av,_max,_min,centr,min_dist):
    '''
    This function find the nearest point to preliminary index finger on approximation image of hand.
    Args:
        p_approx: array of points, approximation of hand
        point: tuple of 2, index finger position
        av: tuple of 2, negative palm direction
        centr:tuple of 2, the center of hand
        _index_a : cosine angle limit of index, only points with cosine values lower than this is considered.
    Return:
        tuple of 2,the point's co-ordinate
    '''
    p = (0,0)
    for i in range(p_approx.shape[0])[::-1]:
        dist = mcv.distance(p_approx[i-1][0],point)
        if dist>min_dist:
            continue
        dir = mcv.subt(p_approx[i-1][0],centr)
        if not mcv.zero(dir):
            angle = mcv.angle(dir,av)
            if angle>_max or angle<_min:
                continue
        ca,cb = mcv.convex(p_approx[i][0],p_approx[i-1][0],p_approx[i-2][0])
        if cb:
            min_dist = dist
            p = p_approx[i-1][0] 
    return tuple(p)

def findFingers(tP,iP,hull,last_i,centr,av,p_approx):
    '''
    This function use angle to find thumb and index on convex hull
    Args:
        tP,iP: thumb and index parameter
        hull: convex hull of hand
        last_i: from where to search, the number of leftmost point
        centr: hand centr
        av: negative palm direction
        p_approx: approximation of hand
    Return: tuple of 4, if not found return (0,0)
        thumb on convex hull
        thumb on p_approx
        index on convex hull
        index on p_approx
    '''
    _index_l = iP['l']
    _index_a = iP['a']
    _index_md = iP['d']
    _thumb_l = tP['l']
    _thumb_a = tP['a']
    _thumb_md = tP['d']
    thumb = (0,0)
    index = (0,0)
    p_thumb = (0,0)
    p_index = (0,0)
    for i in range(last_i,hull.shape[0]-1):
        end = tuple(hull[i][0])
        start = tuple(hull[i+1][0])
        length = mcv.distance(start,end)
# find thumb
        if length>_thumb_l:
            if mcv.angle(mcv.subt(end,centr),av) < _thumb_a:
                thumb = end
                p_thumb = findNearest(p_approx,thumb,av,_thumb_a,_index_a,centr,_thumb_md)
                _thumb_l = 1000
# find index                    
        if length>_index_l:
            c_angle = mcv.angle(mcv.subt(end,centr),av)
            if c_angle<_index_a:
                index = end
                p_index = findNearest(p_approx,index,av,_index_a,-1,centr,_index_md)
                break
            c_angle = mcv.angle(mcv.subt(start,centr),av)
            if c_angle<_index_a:
                index = start
                p_index = findNearest(p_approx,start,av,_index_a,-1,centr,_index_md)
                break
    return thumb,p_thumb,index,p_index

def checkMiddle(p_thumb,p_index,p_approx,no,conv_th):
    '''
    This function check if the p_index is real, or it is the middle finger, and return the real index position
    from thumb to index, the first points after a concave and before another concave 
    are considered to represent index. 
    Args:
        p_thumb,p_index: previously detected position
        p_approx: array of points, approximation of hand
        no: int, the number of current frame in the video, helps to check which frame is of this condition
        conv_th: to tell whether a convex is small or not
    output: tuple of 2 ints, the real index, If nothing in between, we still return p_index.
    '''
    flag = False
    indexl = []
    prevprev = -1
    prev = -1
    enter = False
    after_concave=0
    pr_index = p_index
    for i in np.append(p_approx[::-1],p_approx[::-1],axis = 0):
        i=i[0]
        if mcv.equal(i,p_thumb):
            flag = True
            count = 1
            enter = True
        elif mcv.equal(i,p_index):
            flag = False
            if enter:
                break
        if flag:
            if count<0:
                small,conv = mcv.convex(prevprev,prev,i,conv_th)
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
        if len(indexl) > 1:
            indexl = np.array(indexl)
            pr_index = (int(np.mean(indexl[:,0])), int(np.mean(indexl[:,1])))
        else:
            pr_index = tuple(indexl[0])
    return pr_index
def preIndexUD(thresh,img,cntAreaTh,preprocess,threshInc,threshDec):
    ret = []
    _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnt = mcv.largest(cntAreaTh,contours)
    if len(cnt)<3: return ret
    cnt = np.array(cnt)
#     cnt = np.concatenate((cnt,cnt), axis=0)
    if preprocess==2:
        cv2.drawContours(img,[cnt],0,colors.colors['green'],1)
    min = cnt[-1][0][1]
    dir = 1
    for i in range(len(cnt))[::-1]:
        cur = cnt[i][0][1]
        if dir ==1:
            if cur<min:
                min=cur
            elif cur-min > threshInc:
                dir = 0
                start = i
                max = cur
                maxx = cnt[i][0][0]
        elif dir == 0:
            if cur>max:
                max = cur
                maxx = cnt[i][0][0]
            elif max-cur> threshDec:
                dir = 1
                if cnt[i][0][0]<maxx:
                    ret.append(cnt[i:start])
                if len(ret)>1:
                    if preprocess==2:
                        cv2.drawContours(img,[ret[0]],0,colors.colors['pink'],1)
                        cv2.drawContours(img,[ret[1]],0,colors.colors['pink'],1)
                    break
                min = cur
    return ret

def preIndex(thresh,img,no,cntAreaTh,approx_e,bottoms,_thumb,_index,root,output,conv_th,preprocess):
    '''
    This function finds the index, return its position
    Args:
        thresh: Grayscale black and white image after background subtraction
        img: the original RGB image( used to draw results on)
        no: int, number of current frame
        cntAreaTh: the minimal area of a hand
        approx_e: degree of approximation, the bigger the closer to original
        bottoms: include 5 values help to find the wrist line
        _thumb: include 2 values, l to set the minimal length of edge that we check, a to set the max cosine of thumb
        _index: include 2 values, l to set the minimal length of edge that we check, a to set the max cosine of index, x to set the minimal x-value of index
        root: path of the window and if we write images, the folder name
        output: -1 means write images, 1 means write videos, 0 means write nothing.
        conv_th:
        preprocess: before real experiment, do some inspect.
    Return:
        tuple of 2, preliminary index finger co-ordinate
        if fail, return (0,0)
    '''
    pr_index=(0,0)
    global timers
    timers=[]
    timers.append(Timer())
    timers.append(Timer())
    # basics
    _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnt = mcv.largest(cntAreaTh,contours)
    if len(cnt)<3: return pr_index
    cnt = np.asarray(cnt)
    hull = cv2.convexHull(np.asarray(cnt),clockwise=False)
    epsilon = approx_e*cv2.arcLength(cnt,True)
    p_approx = cv2.approxPolyDP(cnt,epsilon,True)
    if preprocess==1:
        timers[1].start()
        cv2.drawContours(img,[cnt],0,colors.colors['green'],2)
#         cv2.drawContours(img,[p_approx],0,colors.colors['pink'],2)
        timers[1].stop()
        return (0,0)
    moments = cv2.moments(hull)
    if moments['m00']!=0:
        cx = int(moments['m10']/moments['m00'])
        cy = int(moments['m01']/moments['m00'])
    centr=(cx,cy)
    hull = np.append(hull,[hull[0]],0)
    timers[0].start()
    last_i,leftmost,sym,av = findPalmDir(hull,bottoms['bottom-l'],
                                         bottoms['bottom-l-l'],bottoms['bottom-l-x'],
                                         bottoms['bottom-r-l'],bottoms['bottom-r-dis'],centr)
    timers[0].stop()
    if preprocess==2:
        timers[1].start()
        cv2.circle(img,leftmost,5,colors.colors['yellow'],-1)
        cv2.circle(img,sym,5,colors.colors['yellow'],-1)
        cv2.line(img,centr,mcv.addt(centr,av),colors.colors['pink'],1)
        timers[1].stop()
        return (0,0)        
    if mcv.zero(sym):
        return pr_index
    
    thumb,p_thumb,index,p_index = findFingers(_thumb,_index,hull,last_i,centr,av,p_approx)
    if p_index[0]>0 and not mcv.equal(p_thumb,(0,0)) and not mcv.equal(p_index,p_thumb):
        pr_index = checkMiddle(p_thumb,p_index,p_approx,no,conv_th)
    elif p_index[0]>0:# no thumb found
        pr_index = p_index
    else:# no thumb and no p_index found
        pr_index = index
    
    if preprocess==3:
        cv2.drawContours(img,[p_approx],0,colors.colors['green'],2)
        cv2.drawContours(img,[hull],0,colors.colors['pink'],2)
        cv2.circle(img,centr,5,colors.colors['pink'],-1)
        # axis
        cv2.circle(img,leftmost,5,colors.colors['yellow'],-1)
        cv2.circle(img,sym,5,colors.colors['yellow'],-1)
        cv2.line(img,centr,mcv.addt(centr,av),colors.colors['pink'],1)
        # fingers
        cv2.circle(img,thumb,7,colors.colors['pink'],-1)
        cv2.circle(img,index,6,colors.colors['blue'],-1)
        cv2.circle(img,p_thumb,5,colors.colors['green'],-1)
        cv2.circle(img,p_index,4,colors.colors['red'],-1)
        # precise
        cv2.circle(img,pr_index,3,colors.colors['white'],-1)

    if output < 0:
        cv2.imwrite(root+"/"+str(no)+'.png',img)    
        if mcv.equal(pr_index,(0,0)):
            print "(0,0) : "+root+"/"+str(no)+'.png'

    return pr_index

def prinTimers():
    global timers
    print "prlc timers: "
    for timer in timers:
        timer.cal()
if __name__ == '__main__':
    pass