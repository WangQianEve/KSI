'''
Created on Aug 15, 2017
@author: qian
'''
# my modules
from BackgroundSubtraction import BackgroundSubtractor
import PreciseLocating as prlc
import RoughLocating as lcid
import mcv
import colors
import depth as dp
import display
import keylogger

# public modules
import cv2
from pymouse import PyMouse
import json
from imutils.video import FPS
import collections
import argparse
from multiprocessing import Manager, Process
from timer import Timer
import numpy as np
import time
from numpy.core.defchararray import index
def setCam(cap0,gain=None,w=None,h=None,fps=None):
    if w is not None:
        cap0.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    if h is not None:
        cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    if fps is not None:
        cap0.set(cv2.CAP_PROP_FPS, fps)
    if gain is not None:
        cap0.set(cv2.CAP_PROP_GAIN,gain)

def setGain(frame0,frame1,gain,cap0,cap1,crop,standardBrightness=150,threshBrightness=5):
    # get gain
    lower = 0.2
    higher = 0.8
    mini = 0.05
    while True:
        cv2.imshow("frame0",frame0)
        k=cv2.waitKey(1)
        if k==27:
            break
        aveBrightness = mcv.aveBrightness(frame0)
        print "[calibration] aveBrightness 0 "+ str(aveBrightness)
        distBrightness = aveBrightness - standardBrightness
        if abs(distBrightness) < threshBrightness: # gain get
            break
        if distBrightness > 0:
            higher =gain[0]
            gain[0] = (gain[0] + lower)/2
            setCam(cap0, gain=gain[0])
        else:
            lower = gain[0]
            gain[0] = (gain[0] + higher)/2
            setCam(cap0, gain=gain[0])
        print "[calibration] tring cam 0 gain "+str(gain[0])
        if abs(higher-lower) < mini:
            break
        ret,framenew=cap0.read()
        framenew = framenew[crop[0][2]:crop[0][3] , crop[0][0]:crop[0][1]]
        while not mcv.diff(framenew,frame0):
            ret,framenew=cap0.read()
            framenew = framenew[crop[0][2]:crop[0][3] , crop[0][0]:crop[0][1]]
            cv2.imshow("frame0",framenew)
            k=cv2.waitKey(1)
        frame0 = framenew

    gain[1] = gain[0]
    lower = 0.2
    higher = 0.8

    while True:
        cv2.imshow("frame1",frame1)
        k=cv2.waitKey(1)
        if k==27:
            break
        aveBrightness = mcv.aveBrightness(frame1)
        print "[calibration] aveBrightness 1 "+ str(aveBrightness)
        distBrightness = aveBrightness - standardBrightness
        if abs(distBrightness) < threshBrightness: # gain get
            break
        if distBrightness > 0:
            higher =gain[1]
            gain[1] = (gain[1] + lower)/2
            setCam(cap1, gain=gain[1])
        else:
            lower = gain[1]
            gain[1] = (gain[1] + higher)/2
            setCam(cap1, gain=gain[1])
        print "[calibration] tring cam 1 gain "+str(gain[1])
        if abs(higher-lower) < mini:
            break
        ret,framenew=cap1.read()
        framenew = framenew[crop[1][2]:crop[1][3] , crop[1][0]:crop[1][1]]
        while not mcv.diff(framenew,frame1):
            ret,framenew=cap1.read()
            framenew = framenew[crop[1][2]:crop[1][3] , crop[1][0]:crop[1][1]]
            cv2.imshow("frame1",framenew)
            k=cv2.waitKey(1)
        frame1 = framenew

def mainLoop(par,kill,key,user,argMode):
    if par['step']<calibration['final']:
        cv2.namedWindow('frame0', cv2.WINDOW_NORMAL)
        cv2.namedWindow('frame1', cv2.WINDOW_NORMAL)
    # load parameters
    with open("./configuration/"+user+".json") as json_data_file:
        data = json.load(json_data_file)
        para = data['ctrl']
        depth = data['depth']
        handBgstPara0 = data['hand'][0]
        handBgstPara1 = data['hand'][1]
        prIdPara0 = data['lc'][0]
        prIdPara1 = data['lc'][1]

    # set system paramteres
    mouse = PyMouse()
    width,height=mouse.screen_size()
    camw = 320
    camh = 240
    camfps = 200
    crop = [[0,150,30,240],[160,310,30,240]]
    active = [0,130,125,225]
    activeShape = (active[1]-active[0],active[3]-active[2])
    mode = argMode # 0 for absolute; 1 for relative

    sizex = 15
    sizey = 30
    # set user parameters
    # cams
    par['gain'] = para['gain']
    # hands
    par['sbsThreshL'] = [handBgstPara0['sbsThreshL'],handBgstPara1['sbsThreshL']]
    par['sbsThreshH'] = [handBgstPara0['sbsThreshH'],handBgstPara1['sbsThreshH']]
    par['sbsGause'] = [handBgstPara0['sbsGause'],handBgstPara1['sbsGause']]
    # fingertips
    par['ydis'] = prIdPara0['ydis']
    par['yth'] = prIdPara0['yth']
    # depth
    par['touch']=depth['thresh']

    # set cams
    cap0 = cv2.VideoCapture(1)
    setCam(cap0,para['gain'][0],camw,camh,camfps)
    cap1 = cv2.VideoCapture(2)
    setCam(cap1,para['gain'][1],camw,camh,camfps)

    # to be checked
    # initialize variables
    dat=dict()
    dat['pointing'] = True
    dat['depth'] = 0
    dat['absDepth'] = 0
    dat['touch'] = False
    dat['position'] = [0,0]
    pre0=(0,0)
    pre1=(0,0)
    preF0=[0,0]
    preF1=[0,0]
    plane = False
    dis01 = (0,0)
    manule = False
    x0,y0,x1,y1 = [collections.deque() for i in xrange(4)]
    setYth = False
    # initialize modules
    dp.init(user, camw)
    handBgst0 = BackgroundSubtractor(type='sbs',sbsThreshL=handBgstPara0['sbsThreshL'],sbsThreshH=handBgstPara0['sbsThreshH'],gause=handBgstPara0['sbsGause'])
    handBgst1 = BackgroundSubtractor(type='sbs',sbsThreshL=handBgstPara1['sbsThreshL'],sbsThreshH=handBgstPara1['sbsThreshH'],gause=handBgstPara1['sbsGause'])

    # options
    if par['step']>calibration['getBg']:
        handBgst0.setBgM(cap0,20)
        handBgst1.setBgM(cap1,20)

    print "tracking..."
    fps = FPS().start()

    while True:
        if kill['kill']:
            break
        fps.update()

        if par['step']==calibration['final']:
            if key['status']:
                if key['info']=="<esc>":
                    break
                elif key['info']=='<space>' and dat['pointing']:
                    mouse.click(mouse.position()[0],mouse.position()[1], 1)
                elif key['info']=='<tab>':
                    dat['pointing'] = not dat['pointing']
                    dat['position'] = list(mouse.position())
                key['status']=False
        # image processing
        ret, _frame0 = cap0.read()
        ret, _frame1 = cap1.read()

        if par['step']==calibration['position']:
            cv2.line(_frame0,(crop[0][0],crop[0][2]),(crop[0][0],crop[0][3]),colors.colors['pink'],1)
            cv2.line(_frame0,(crop[0][1],crop[0][2]),(crop[0][1],crop[0][3]),colors.colors['pink'],1)
            cv2.line(_frame0,(crop[0][0],crop[0][2]),(crop[0][1],crop[0][2]),colors.colors['pink'],1)
            cv2.line(_frame0,(crop[0][0],crop[0][3]),(crop[0][1],crop[0][3]),colors.colors['pink'],1)
            #
            cv2.line(_frame1,(crop[1][0],crop[1][2]),(crop[1][0],crop[1][3]),colors.colors['pink'],1)
            cv2.line(_frame1,(crop[1][1],crop[1][2]),(crop[1][1],crop[1][3]),colors.colors['pink'],1)
            cv2.line(_frame1,(crop[1][0],crop[1][2]),(crop[1][1],crop[1][2]),colors.colors['pink'],1)
            cv2.line(_frame1,(crop[1][0],crop[1][3]),(crop[1][1],crop[1][3]),colors.colors['pink'],1)
            #
            cv2.line(_frame0,(active[0],active[2]),(active[0],active[3]),colors.colors['green'],2)
            cv2.line(_frame0,(active[1],active[2]),(active[1],active[3]),colors.colors['green'],2)
            cv2.line(_frame0,(active[0],active[2]),(active[1],active[2]),colors.colors['green'],2)
            cv2.line(_frame0,(active[0],active[3]),(active[1],active[3]),colors.colors['green'],2)

            cv2.imshow("frame0",_frame0)
            cv2.imshow("frame1",_frame1)
            k=cv2.waitKey(1)
            if k==27: # esc
                break
            if k==195: # f6
                par['step'] = calibration['gain']
            continue

        frame0 = _frame0[crop[0][2]:crop[0][3] , crop[0][0]:crop[0][1]]
        frame1 = _frame1[crop[1][2]:crop[1][3] , crop[1][0]:crop[1][1]]

        if par['step']==calibration['gain'] and not manule:
            setGain(frame0,frame1,para['gain'],cap0,cap1,crop)
            print "[calibration] cams gain SET "+ str(para['gain'])
            par['gain']=para['gain']
            k=cv2.waitKey()
            if k==27:
                break
            if k==192: #f3
                manule = True
            if k==195:
                par['step'] = calibration['threshL0']
            continue

        if par['step']==calibration['threshL0']:
            gray = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
            valid = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)[1]
            grayBlur = cv2.blur(gray,(par['sbsGause'][0],par['sbsGause'][0]))
            thresh = cv2.threshold(grayBlur, par['sbsThreshL'][0], 255, cv2.THRESH_BINARY)[1]

            cv2.imshow("frame0",frame0)
            cv2.imshow("valid",valid)
            cv2.imshow("thresh",thresh)
            preFingers0 = lcid.preIndexUD(thresh.copy(),frame0, 300,
                                        2,prIdPara0['Uthresh'],prIdPara0['Dthresh'])
            if len(preFingers0)==0:
                continue
            elif len(preFingers0) ==1:
                finIndex0 = prlc.prlc("notsmooth",cnt = preFingers0[0])
            else:
                finIndex0 = prlc.prlc("notsmooth",cnt = preFingers0[1])
            indexRecc = mcv.getRec(finIndex0, sizex,sizey, thresh.shape)
            mthresh = thresh[indexRecc[2]:indexRecc[3] , indexRecc[0]:indexRecc[1]]
            mvalid =valid[indexRecc[2]:indexRecc[3] , indexRecc[0]:indexRecc[1]]
            cv2.imshow("area",mthresh)
            cv2.imshow("areaT",mvalid)
            broken = mcv.broken(mthresh,sizex*sizey/25)
            area = mcv.area(mthresh)
            areaT = mcv.area(mvalid)
            if broken or area<areaT*0.6:
                par['sbsThreshL']=[ par['sbsThreshL'][0]-2, par['sbsThreshL'][1] ]
            cv2.rectangle(frame0,(indexRecc[0],indexRecc[2]),(indexRecc[1],indexRecc[3]),colors.colors['green'])
            cv2.putText(frame0,str(par['sbsThreshL'][0])+"  "+str(broken),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.putText(frame0,str(area)+"  "+str(areaT),(10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.imshow("frame0",frame0)
            k= cv2.waitKey(1)
            if k==194:#f5 reset
                par['sbsThreshL']=[ 100, par['sbsThreshL'][1] ]
            if k==195:
                par['sbsThreshL']=[ par['sbsThreshL'][0]-2, par['sbsThreshL'][1] ]
                par['step'] = calibration['threshL1']
            if k==27:
                break
            continue

        if par['step']==calibration['threshL1']:
            gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            valid = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)[1]
            grayBlur = cv2.blur(gray,(par['sbsGause'][1],par['sbsGause'][1]))
            thresh = cv2.threshold(grayBlur, par['sbsThreshL'][1], 255, cv2.THRESH_BINARY)[1]

            cv2.imshow("frame1",frame1)
            cv2.imshow("valid",valid)
            cv2.imshow("thresh",thresh)
            preFingers1 = lcid.preIndexUD(thresh.copy(),frame1, 300,
                                        2,prIdPara1['Uthresh'],prIdPara1['Dthresh'])
            if len(preFingers1)==0:
                continue
            elif len(preFingers1) ==1:
                finIndex1 = prlc.prlc("notsmooth",cnt = preFingers1[0])
            else:
                finIndex1 = prlc.prlc("notsmooth",cnt = preFingers1[1])
            indexRecc = mcv.getRec(finIndex1, sizex,sizey, thresh.shape)
            mthresh = thresh[indexRecc[2]:indexRecc[3] , indexRecc[0]:indexRecc[1]]
            mvalid =valid[indexRecc[2]:indexRecc[3] , indexRecc[0]:indexRecc[1]]
            cv2.imshow("area",mthresh)
            cv2.imshow("areaT",mvalid)
            broken = mcv.broken(mthresh,sizex*sizey/25)
            area = mcv.area(mthresh)
            areaT = mcv.area(mvalid)
            if broken or area<areaT*0.6:
                par['sbsThreshL']=[ par['sbsThreshL'][0],par['sbsThreshL'][1]-2 ]
            cv2.rectangle(frame1,(indexRecc[0],indexRecc[2]),(indexRecc[1],indexRecc[3]),colors.colors['green'])
            cv2.putText(frame1,str(par['sbsThreshL'][1])+"  "+str(broken),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.putText(frame1,str(area)+"  "+str(areaT),(10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.imshow("frame1",frame1)
            k= cv2.waitKey(1)
            if k==194:#f5 reset
                par['sbsThreshL']=[ par['sbsThreshL'][0],100 ]
            if k==195:
                par['sbsThreshL']=[ par['sbsThreshL'][0],par['sbsThreshL'][1]-2 ]
                handBgst0.setThresh(par['sbsThreshL'][0],par['sbsThreshH'][0])
                handBgst1.setThresh(par['sbsThreshL'][1],par['sbsThreshH'][1])
                par['step'] = calibration['getBg']
            if k==27:
                break
            continue

        if par['step']==calibration['getBg']:
            cv2.imshow("frame0",frame0)
            cv2.imshow("frame1",frame1)
            k = cv2.waitKey(1)
            if k==27:
                break
            elif k==192: #f3
                handBgst0.setBgM(cap0,20)
                handBgst1.setBgM(cap1,20)
                print "[calibration] bg done"
            elif k==195:
                par['step']=calibration['threshH']
            continue

        hand0 = handBgst0.bgst(_frame0)
        hand1 = handBgst1.bgst(_frame1)
        hand0 = hand0[crop[0][2]:crop[0][3] , crop[0][0]:crop[0][1]]
        hand1 = hand1[crop[1][2]:crop[1][3] , crop[1][0]:crop[1][1]]
        if par['step']==calibration['threshH']:
            if not mcv.clean(hand0):
                par['sbsThreshH']=[par['sbsThreshH'][0]-2,par['sbsThreshH'][1]]
                handBgst0.setThresh(par['sbsThreshL'][0],par['sbsThreshH'][0])
                print par['sbsThreshH']
            if not mcv.clean(hand1):
                par['sbsThreshH']=[par['sbsThreshH'][0],par['sbsThreshH'][1]-2]
                handBgst1.setThresh(par['sbsThreshL'][1],par['sbsThreshH'][1])
                print par['sbsThreshH']
            cv2.imshow("frame0",_frame0)
            cv2.imshow("frame1",_frame1)
            cv2.imshow("hand0",hand0)
            cv2.imshow("hand1",hand1)
            k = cv2.waitKey(1)
            if k==27:
                break
            elif k==194: #f5
                par['sbsThreshH']=[255,255]
                handBgst0.setThresh(par['sbsThreshL'][0],par['sbsThreshH'][0])
                handBgst1.setThresh(par['sbsThreshL'][1],par['sbsThreshH'][1])
            elif k==195:
                print "[calibration] set threshHigh "+str(par['sbsThreshH'])
                par['step']=calibration['yth']
            continue

        preFingers0 = lcid.preIndexUD(hand0,frame0, 300,
                                    par['step'],prIdPara0['Uthresh'],prIdPara0['Dthresh'])
        preFingers1 = lcid.preIndexUD(hand1,frame1, 300,
                                    par['step'],prIdPara1['Uthresh'],prIdPara1['Dthresh'])

        # locating tip
        finThumb0 = (0,0)
        finThumb1 = (0,0)
        if len(preFingers0)==0:
            finIndex0 = pre0
        elif len(preFingers0) ==1:
            finIndex0 = prlc.prlc("notsmooth",cnt = preFingers0[0],img = frame0,textPos=40)
        else:
            finThumb0 = prlc.prlc("notsmooth",cnt = preFingers0[0],img = frame0,textPos=20)
            finIndex0 = prlc.prlc("notsmooth",cnt = preFingers0[1],img = frame0,textPos=40)
            cv2.putText(frame0,str(mcv.ptoint(finIndex0)[0])+" "+str(mcv.ptoint(finIndex0)[1]),(10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.putText(frame0,str(mcv.ptoint(finThumb0)[0])+" "+str(mcv.ptoint(finThumb0)[1]),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.circle(frame0,mcv.ptoint(finIndex0),2,colors.colors['white'],-1)
            cv2.circle(frame0,mcv.ptoint(finThumb0),2,colors.colors['white'],-1)
            if finIndex0[1]-finThumb0[1] < prIdPara0['ydis']  and finThumb0[1]>prIdPara0['yth']:
                finIndex0 = finThumb0
            if finIndex0[1] < finThumb0[1]:
                finIndex0 = finThumb0
        cv2.circle(frame0,mcv.ptoint(finIndex0),3,colors.colors['yellow'],-1)
        pre0=finIndex0

#         continue
        if len(preFingers1)==0:
            finIndex1 = pre1
        elif len(preFingers1) ==1:
            finIndex1 = prlc.prlc("notsmooth",cnt = preFingers1[0],img = frame1, textPos=40)
        else:
            finThumb1 = prlc.prlc("notsmooth",cnt = preFingers1[0],img = frame1, textPos=20)
            finIndex1 = prlc.prlc("notsmooth",cnt = preFingers1[1],img = frame1, textPos=40)
            if par['step']==calibration['yth']:
                cv2.putText(frame1,str(mcv.ptoint(finIndex1)[0])+" "+str(mcv.ptoint(finIndex1)[1]),(10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
                cv2.putText(frame1,str(mcv.ptoint(finThumb1)[0])+" "+str(mcv.ptoint(finThumb1)[1]),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
                cv2.circle(frame1,mcv.ptoint(finIndex1),2,colors.colors['white'],-1)
                cv2.circle(frame1,mcv.ptoint(finThumb1),2,colors.colors['white'],-1)
            if mcv.distance(finIndex0, mcv.subt(finThumb1, dis01)) < mcv.distance(finIndex0, mcv.subt(finIndex1, dis01)): ## dis
                finIndex1 = finThumb1
        cv2.circle(frame1,mcv.ptoint(finIndex1),3,colors.colors['yellow'],-1)
        pre1=finIndex1

        if par['step']==calibration['yth']:
            cv2.rectangle(_frame0,(active[0],active[2]),(active[1],active[3]),colors.colors['green'])
            if setYth:
                par['yth']=max(finThumb0[1],par['yth'])
            cv2.putText(frame0,str(setYth)+" "+str(par['yth']),(10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.imshow("frame0",frame0)
            cv2.imshow("frame1",frame1)
            k=cv2.waitKey(1)
            if k==192:#f3
                setYth = not setYth
            if k==194:#f5
                par['yth']=active[2]-crop[0][2]
            if k==195:
                par['step']=calibration['plane']
            if k==27:
                break
            continue

        finIndex0 = [finIndex0[0]+crop[0][0], finIndex0[1]+crop[0][2]]
        finIndex1 = [finIndex1[0]+crop[1][0], finIndex1[1]+crop[1][2]]

        if par['step']==calibration['plane']:
            preF0=finIndex0
            preF1=finIndex1
            if plane:
                x0.append(finIndex0[0])
                y0.append(finIndex0[1])
                x1.append(finIndex1[0])
                y1.append(finIndex1[1])
            dep = dp.depthEstimate(finIndex0[0], finIndex0[1], finIndex1[0], finIndex1[1])
            cv2.putText(frame0,str(dep),(10,80), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.rectangle(_frame0,(active[0],active[2]),(active[1],active[3]),colors.colors['green'])
            cv2.imshow("frame0",frame0)
            cv2.imshow("frame1",frame1)
            k=cv2.waitKey(1)
            if k==27:
                break
            if k==192:# f3
                if plane:
                    print "end recording"
                    dp.keybplaneCalcN((x0,y0,x1,y1)) ## para
                    x0,y0,x1,y1 = [collections.deque() for i in xrange(4)]
                    plane = False

                else:
                    print "start recording"
                    plane = True
            if k==195:
                par['step']=calibration['depth']
            continue

        dp.getTouch(finIndex0,finIndex1,preF0,preF1,par['alpha'],dat,depth['l'],depth['h'],par['touch'],active)

        if par['step']==calibration['depth']:
            preF0=finIndex0
            preF1=finIndex1
            cv2.circle(_frame0,(int(finIndex0[0]),int(finIndex0[1])),3,colors.colors['yellow'],-1)
            cv2.circle(_frame1,(int(finIndex1[0]),int(finIndex1[1])),3,colors.colors['yellow'],-1)
            cv2.rectangle(_frame0,(active[0],active[2]),(active[1],active[3]),colors.colors['green'])
            cv2.putText(_frame0,str(dat['depth']),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.putText(_frame0,str(dat['touch']),(10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.putText(_frame0,str(dat['position'][0])+" "+str(dat['position'][1]),(10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.imshow("frame0",_frame0)
            cv2.imshow("frame1",_frame1)
            k = cv2.waitKey(1)
            if k==27:
                break
            continue

        if dat['touch'] and dat['pointing'] and par['step']==calibration['final']:
            if mode==0: # absolute
                dat['position'][0]=finIndex0[0]
                dat['position'][1]=finIndex0[1]
                dat['position'][0]= (active[1]-dat['position'][0]+0.0) *width / activeShape[0]
                dat['position'][1]= (active[3]-dat['position'][1]+0.0) *height/ activeShape[1]
                mouse.move(dat['position'][0],dat['position'][1])

            if mode==1: # relative
                delta = list(mcv.subt( preF0,finIndex0 ))
                delta[0]=delta[0]*(width+0.0)/activeShape[0]
                delta[1]=delta[1]*(height+0.0)/activeShape[1]
                dat['position'] = list(mcv.addt(dat['position'] , delta))
                if dat['position'][0]>width:
                    dat['position'][0] = width
                if dat['position'][1]>height:
                    dat['position'][1] = height
                if dat['position'][0]<0:
                    dat['position'][0] = 0
                if dat['position'][1]<0:
                    dat['position'][1] = 0
                mouse.move(dat['position'][0],dat['position'][1])

        preF0=finIndex0
        preF1=finIndex1

    para['gain']=par['gain']
    handBgstPara0['sbsThreshL']=par['sbsThreshL'][0]
    handBgstPara1['sbsThreshL']=par['sbsThreshL'][1]
    handBgstPara0['sbsThreshH']=par['sbsThreshH'][0]
    handBgstPara1['sbsThreshH']=par['sbsThreshH'][1]
    prIdPara0['yth']=par['yth']
    with open("./configuration/"+user+".json", 'w') as f:
        js = {'ctrl':para,
              'depth':depth,
              'hand':[handBgstPara0,handBgstPara1],
              'lc':[prIdPara0,prIdPara1]}
        json.dump(js,f)
        print("write to file")

    fps.stop()
    print("[TEST1] elasped time: {:.2f}".format(fps.elapsed()))
    print("[TEST1] approx. FPS: {:.2f}".format(fps.fps()))

    kill['kill'] = True
    cap0.release()
    cap1.release()
    cv2.destroyAllWindows()

import os
import shutil

def initializeUser(user):
    if os.path.exists("./configuration/"+user+".dat"):
        raise NameError("user exists, please use another name")
    if not os.path.exists("./configuration/"+user+".json"):
        shutil.copy("./configuration/default.json", "./configuration/"+user+".json" )

if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-u", "--user", type=str, default="qian",
        help="Which config file to load")
    ap.add_argument("-s", "--step", type=str, default="position",
        help="Which step")
    ap.add_argument("-m", "--mode", type=int, default=1,
        help="1 for relative 0 for absolute")
    args = vars(ap.parse_args())
#     initializeUser(args['user'])

    global calibration
    calibrationIndexes = ['position','gain','threshL0','threshL1','getBg','threshH','yth','plane','depth','final']
    calibration = {}
    for i in xrange(len(calibrationIndexes)):
        calibration[calibrationIndexes[i]] = i

    # variables for multi-processing
    manager = Manager()
    key = manager.dict() # get keyboard events
    kill = manager.dict() # killing other processes or not
    par = manager.dict() # help adjust parameters

    key['status']=False
    key['info']=""

    kill['kill']=False

    par['step'] = calibration[args['step']]
    par['gain'] = [0,0]
    par['sbsThreshL']=[0,0]
    par['sbsThreshH']=[0,0]
    par['sbsGause']=[0,0]
    par['threshChange']=False
    par['ydis']=[0,0]
    par['alpha']=0.1
    par['yth']=[0,0]
    par['touch']=0

    if args['step']=='final':
        p = Process(target=keylogger.log, args=(key,kill))
        p.start()

    global timers
    timers = [Timer() for i in xrange(4)]
    mainLoop(par, kill, key, args['user'], args['mode'])
