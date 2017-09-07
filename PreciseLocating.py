'''
@author: qian
'''
import cv2
import mcv
import numpy as np    
import colors
import signalpro as spo
from timer import Timer
def boxCorner(cnt):
    '''
    Called by prlc(). This function use a box to contain the fingertip and use topleft point as anchor to determine the track point.
    cnt: points that represent the fingertip
    pos: the distance of track point from anchor(box corner).
    '''
    if len(cnt)<3:
        return [0,0]
    x,y,w,h = cv2.boundingRect(cnt)
    return [x+w,y+h]

def topLine(frame,edges,preprocess):
    '''
    Called by prlc(). This function find the rightmost line that has white pixels, calculate the average y coordinate, and return the 2-d coordinate of the point
    frame: Gray scale binary color image, with only finger tip white.
    edges: the number of sample points.
    preprocess: stage
    output: [x,y] the point
    '''
    xs=[]
    ys=[]
    lines=[]
    flag = False
    for y in range(frame.shape[0])[::-1]:
        if flag:
            break
        validr=False
        for x in range(frame.shape[1]):
            c = frame[y][x]
            if c[0]>0:
                xs.append(x)
                ys.append(y)
                validr=True
        if validr:
            lines.append(y)
        if len(xs)>edges:
            flag = True
    if len(xs)==0: return [0,0]
#     if preprocess==4:
#         print len(lines)
    return [ int(np.mean(xs)), int(np.mean(ys)) ]

def prlc(type,cnt=0,img=0,wlen=10,frame=0,area=0,pos=0,edges=6,preprocess=0,textPos=40):
    global timer1,timer2,black,gcnt
    '''
    Function: find the tracking point from the small image around the finger tip
    Args:
        frame: Grayscale binary color image, after background subtraction image of fingertip area
        type: string, "box" or "conv", choose method
        area: int, the minimal area when finding the biggest contour around fingertip
        pos: int, the distance from the corner thatwe use in box method, 
        edges: int, the number of points to sample in method conv
        preprocess: int, preprocess stage
        windowName: if preprocess in stage 4, show contours and convex hull of nail.
    output:
        [x,y] the relative co-ordinate of the track point. If not found, return [0,0]
    '''
    if type=="box":
        _, contours, hierarchy = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cnt = mcv.largest(area,contours)
        return boxCorner(cnt, pos)
    elif type=="conv":
        _, contours, hierarchy = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cnt = mcv.largest(area,contours)
        if len(cnt)<3: return [0,0]
        hull = cv2.convexHull(np.asarray(cnt),clockwise=False)
        img = np.zeros(frame.shape,np.uint8)
        cv2.drawContours(img,[hull],0,colors.colors['white'],1)
        return topLine(img,edges,preprocess)
    elif type=="debug":
        _, contours, hierarchy = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cnt = mcv.largest(area,contours)
        if len(cnt)<3: return [0,0]
        hull = cv2.convexHull(np.asarray(cnt),clockwise=False)
        img = np.zeros(frame.shape,np.uint8)
        cv2.drawContours(img,[hull],0,colors.colors['white'],1)
        return topLine(img,edges,preprocess),img
    elif type=="smooth":
        starty = cnt[0][0][1]
        i=-1
        for i in range(len(cnt)):
            cury = cnt[i][0][1]
            if starty-cury>5:
                break
        x = np.hstack(cnt[:i,:,0])
        y = np.hstack(cnt[:i,:,1])
        if len(x)<wlen:
            pwlen = len(x)
        else:
            pwlen = wlen
        sx=spo.smooth(x,window_len=pwlen,window='blackman')[pwlen-1:]
        sy=spo.smooth(y,window_len=pwlen,window='blackman')[pwlen-1:]
        sm = np.array([(int(sx[i]),int(sy[i])) for i in range(len(sx))])
        if preprocess==3:
            cv2.drawContours(img,[cnt],0,colors.colors['green'],1)
            cv2.drawContours(img,[sm],0,colors.colors['pink'],1)
        img = np.zeros(img.shape,np.uint8)
        cv2.drawContours(img,[sm],0,colors.colors['white'],1)
        preIdRec1 = mcv.getRec(sm[0],20,img.shape[0:2])
        img = img[ preIdRec1[2]:preIdRec1[3],preIdRec1[0]:preIdRec1[1]]
#         cv2.imshow("f",img)
#         cv2.waitKey(1)
        a = topLine(img,edges,preprocess)
        return (preIdRec1[0]+int(a[0]),preIdRec1[2]+int(a[1]))
    elif type=="notsmooth":
        starty = cnt[0][0][1]
        startx = cnt[0][0][0]
        endx = startx
        endi = -1
        max = starty
        maxi = 0
        for i in range(len(cnt)):
            cury = cnt[i][0][1]
            if cury>max:
                max = cury
                maxi = i
            if starty>cury:
                endx = cnt[i][0][0]
                endi = i
                break
        return boxCorner(cnt[:endi])
        return [ (endx+startx)/2, max ]
    
    elif type=="notsmoothbad":
        starty = cnt[0][0][1]
        max = starty
        maxi = 0
        for i in range(len(cnt)):
            cury = cnt[i][0][1]
            if cury>max:
                max = cury
                maxi = i
            if starty>cury:
                break
        if black is None:
            black = np.zeros(img.shape,np.uint8)
        cv2.drawContours(black,[cnt],0,colors.colors['white'],1)
        preIdRec1 = mcv.getRec(cnt[maxi][0],20,img.shape[0:2])
        imgg = black[ preIdRec1[2]:preIdRec1[3],preIdRec1[0]:preIdRec1[1]]
#         cv2.imshow("k",imgg)
#         cv2.waitKey(1)
        a = topLine(imgg,edges,preprocess)
        a[0] += preIdRec1[0]
        a[1] += preIdRec1[2]
        if preprocess==4: #prlc
            cv2.drawContours(img,[cnt],0,colors.colors['green'],1)
            cv2.putText(img,str(a[0])+" "+str(a[1]),(10,textPos), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
#         cv2.drawContours(black,[cnt],0,colors.colors['black'],1)
        return a
    else:
        raise NameError("prlc wrong type")
timer1 = Timer()
timer2 = Timer()
black = None
if __name__ == '__main__':
    pass