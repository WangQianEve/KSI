'''
@author: qian
this module need to be init first
'''
import pickle
import signalpro as spo
import numpy as np
from timer import Timer

def depthEstimate(x1,y1,x2,y2):
    '''
    This function calculate depth by given two points
    '''
    global w
    dist=np.sqrt((x1-x2)**2+(y1-y2)**2)
    if dist==0: return 0
    return w*13.2/dist

def keybTouch(x,y,pathBeta):
    '''
    This function gives estimated depth of the plane by given x and y with a file pathBeta
    '''
    global path,betas
    if betas==[]:
        file=open(pathBeta,'rb')
        betas=pickle.load(file)
        file.close()
        
    Z=np.inner(betas[0],[1,x,y])
    return Z

def keybplaneCalc(points,wlen=40,l=24,h=30):
    '''
    This function calculates the keyboard plane using a set of points, file store to pathBeta
    '''
    global path
    x1,y1,x2,y2=points
    dep=depFilter(x1,y1,x2,y2,l,h)
    sx1=spo.smooth(x1,window_len=wlen,window='blackman')
    sy1=spo.smooth(y1,window_len=wlen,window='blackman')
    sx2=spo.smooth(x2,window_len=wlen,window='blackman')
    sy2=spo.smooth(y2,window_len=wlen,window='blackman')
    sdepth=[depthEstimate(sx1[i],sy1[i],sx2[i],sy2[i])  for i in range(len(sx1))]
    X=np.vstack((sx1,sy1)).T
    X=np.hstack((np.ones((X.shape[0],1)),X))
    Y=sdepth
    betas=np.linalg.lstsq(X,Y)
    file=open(path,'wb')
    pickle.dump(betas,file)
    file.close()
    return True

def keybplaneCalcN(points,l=20,h=30):
    '''
    This function calculates the keyboard plane using a set of points, file store to pathBeta
    '''
    global path
    x1,y1,x2,y2=points
    dep=depFilter(x1,y1,x2,y2,l,h)
    sdepth=[depthEstimate(x1[i],y1[i],x2[i],y2[i])  for i in xrange(len(x1))]
    X=np.vstack((x1,y1)).T
    X=np.hstack((np.ones((X.shape[0],1)),X))
    Y=sdepth
    betas=np.linalg.lstsq(X,Y)
    file=open(path,'wb')
    pickle.dump(betas,file)
    file.close()
    return True

def smooth(l,wlen):
    '''
    This function smooth lists.
    input:
        l: list of lists
        wlen: window width
    output:
        list of smoothed lists
    '''
    ret=[]
    for i in l:
        ret.append(spo.smooth(i,window_len=wlen,window='blackman'))
    return ret

def depFilter(x1,y1,x2,y2,l,h):
    '''
    This function change those points pairs to it's previous position whose depth is obviously wrong.
    input:
        x1,y1,x2,y2: tuple of 2, the two points
        l,h: low and high limit of depth
    '''
    depth=[depthEstimate(x1[i],y1[i],x2[i],y2[i]) for i in range(len(x1))]
    pred=depth[0]
    prevx1=x1[0]
    prevy1=y1[0]
    prevx2=x2[0]
    prevy2=y2[0]
    for i in range(len(depth))[::-1]:
        if depth[i]<l or depth[i]>h:
            depth[i]=pred
            x1[i]=prevx1
            y1[i]=prevy1
            x2[i]=prevx2
            y2[i]=prevy2
        else:
            pred=depth[i]
            prevx1=x1[i]
            prevy1=y1[i]
            prevx2=x2[i]
            prevy2=y2[i]
    return depth

def paint3D(ax,sx1,sy1,sdepth):
    ax.plot(sx1, sy1, sdepth, label='parametric curve')
    ax.legend()
    
def printTimer():
    global timers
    print "timers in depth:"
    for i in timers:
        i.cal()

def init(user,pw,pwlen=11,timerN=0):
    '''
    Init function.
    Input:
        proot: root path, where stores the smoothing file
        pwlen: window size for smoothing tracks
        pw: width of image
        timerN: int, number of timers
    '''
    global wlen,path,w,timers,betas
    timers= [Timer() for i in xrange(timerN)]
    wlen = pwlen
    path = "./configuration/"+user+".dat"
    w = pw
    betas = []

def getTouch(finIndex0,finIndex1,preF0,preF1,alpha,dat,l,h,touchRange,active):
    depth=depthEstimate(finIndex0[0],finIndex0[1], finIndex1[0],finIndex1[1])
    if depth<l or depth>h:
        return 
    finIndex0[0]=alpha*finIndex0[0]+(1-alpha)*preF0[0]
    finIndex0[1]=alpha*finIndex0[1]+(1-alpha)*preF0[1]
    finIndex1[0]=alpha*finIndex1[0]+(1-alpha)*preF1[0]
    finIndex1[1]=alpha*finIndex1[1]+(1-alpha)*preF1[1]
    # check active
    if finIndex0[0]<active[0] or finIndex0[0]>active[1] or finIndex0[1]<active[2] or finIndex0[1]>active[3]:
        dat['touch']= False
        return
    sdepth=depthEstimate(finIndex0[0],finIndex0[1], finIndex1[0],finIndex1[1])
    zdepth=keybTouch(finIndex0[0],finIndex0[1],path)
    ddepth=zdepth-sdepth
    dat['depth']=ddepth
    dat['absDepth']=sdepth
    if ddepth>touchRange:
        dat['touch'] = False
    else:
        dat['touch'] = True

def isTouching(x1,y1,x2,y2,dat,l,h,touchRange):
    '''
    Input:
        dat: dict
            below are only for reference:
            touchRange: the height we distinguish touch and lift

            below are variables that we change:
            position: position after smoothing
            depth: relative depth from keyboard
            absDepth: absolute depth value
            touch: is touching or not
        l,h: noise threshold
    '''
    global wlen,root,w
    # filter out noise
    depFilter(x1,y1,x2,y2,l,h)
    
    sx1,sy1,sx2,sy2=smooth([x1,y1,x2,y2],wlen)
    p = len(sx1)/2 
#     p=-1
    sdepth=depthEstimate(sx1[p],sy1[p],sx2[p],sy2[p])
    zdepth=keybTouch(sx1[p],sy1[p],root+"betas.dat")
    ddepth=zdepth-sdepth
    dat['position'] = [sx1[p],sy1[p]]
    dat['depth']=ddepth
    dat['absDepth']=sdepth
    if ddepth>touchRange:
        dat['touch'] = False
    else:
        dat['touch'] = True
