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

def mainLoop(step,kill,key,user,argMode):
    if step<calibration['final']:
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
    crop = [[0,150,30,240],[160,310,30,240]]
    active = [0,130,125,225]
    activeShape = (active[1]-active[0],active[3]-active[2])
    mode = argMode # 0 for absolute; 1 for relative
    alpha = 0.1
    relaScale = 1
    sizex = 15
    sizey = 30
    standardBrightness = 150
    # set cams
    camw = 320
    camh = 240
    camfps = 200
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
    dis01 = (0,0)
    manule = False
    setYth = False
    # initialize modules
    dp.init("standard", camw)
    handBgst0 = BackgroundSubtractor(type='sbs',sbsThreshL=handBgstPara0['sbsThreshL'],sbsThreshH=handBgstPara0['sbsThreshH'],gause=handBgstPara0['sbsGause'])
    handBgst1 = BackgroundSubtractor(type='sbs',sbsThreshL=handBgstPara1['sbsThreshL'],sbsThreshH=handBgstPara1['sbsThreshH'],gause=handBgstPara1['sbsGause'])

    # options
    if step>calibration['getBg']:
        handBgst0.setBgM(cap0,20)
        handBgst1.setBgM(cap1,20)

    print "tracking..."
    fps = FPS().start()

    while True:
        if kill['kill']:
            break
        fps.update()

        if step==calibration['final']:
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

        if step==calibration['position']:
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
                step = calibration['gain']
            continue

        frame0 = _frame0[crop[0][2]:crop[0][3] , crop[0][0]:crop[0][1]]
        frame1 = _frame1[crop[1][2]:crop[1][3] , crop[1][0]:crop[1][1]]

        if step==calibration['gain']:
            setGain(frame0,frame1,para['gain'],cap0,cap1,crop,standardBrightness)
            print "[calibration] cams gain SET "+ str(para['gain'])
            k=cv2.waitKey()
            if k==27:
                break
            elif key == 61:
                standardBrightness += 5
                print "Brightness "+str(standardBrightness)
            elif key ==45:
                standardBrightness -= 5
                print "Brightness "+str(standardBrightness)
            if k==195:
                saveConfig(para, depth, handBgstPara0, handBgstPara1, prIdPara0, prIdPara1, user)
                step = calibration['threshL0']
            continue

        if step==calibration['threshL0']:
            gray = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
            valid = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)[1]
            grayBlur = cv2.blur(gray,(handBgstPara0['sbsGause'],handBgstPara0['sbsGause']))
            thresh = cv2.threshold(grayBlur, handBgstPara0['sbsThreshL'], 255, cv2.THRESH_BINARY)[1]

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
                handBgstPara0['sbsThreshL']=handBgstPara0['sbsThreshL']-2
            cv2.rectangle(frame0,(indexRecc[0],indexRecc[2]),(indexRecc[1],indexRecc[3]),colors.colors['green'])
            cv2.putText(frame0,str(handBgstPara0['sbsThreshL'])+"  "+str(broken),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.putText(frame0,str(area)+"  "+str(areaT),(10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.imshow("frame0",frame0)
            k= cv2.waitKey(1)
            if k==194:#f5 reset
                handBgstPara0['sbsThreshL']= 100
            if k==195:
                handBgstPara0['sbsThreshL']=handBgstPara0['sbsThreshL']-2
                saveConfig(para, depth, handBgstPara0, handBgstPara1, prIdPara0, prIdPara1, user)
                step = calibration['threshL1']
            if k==27:
                break
            continue

        if step==calibration['threshL1']:
            gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            valid = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)[1]
            grayBlur = cv2.blur(gray,(handBgstPara1['sbsGause'],handBgstPara1['sbsGause']))
            thresh = cv2.threshold(grayBlur, handBgstPara1['sbsThreshL'], 255, cv2.THRESH_BINARY)[1]

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
                handBgstPara1['sbsThreshL']= handBgstPara1['sbsThreshL']-2
            cv2.rectangle(frame1,(indexRecc[0],indexRecc[2]),(indexRecc[1],indexRecc[3]),colors.colors['green'])
            cv2.putText(frame1,str(handBgstPara1['sbsThreshL'])+"  "+str(broken),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.putText(frame1,str(area)+"  "+str(areaT),(10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.imshow("frame1",frame1)
            k= cv2.waitKey(1)
            if k==194:#f5 reset
                handBgstPara0['sbsThreshL']=100
            if k==195:
                handBgstPara1['sbsThreshL'] = handBgstPara1['sbsThreshL']-2
                handBgst0.setThresh(handBgstPara0['sbsThreshL'],handBgstPara0['sbsThreshH'])
                handBgst1.setThresh(handBgstPara1['sbsThreshL'],handBgstPara1['sbsThreshH'])
                saveConfig(para, depth, handBgstPara0, handBgstPara1, prIdPara0, prIdPara1, user)
                step = calibration['getBg']
            if k==27:
                break
            continue

        if step==calibration['getBg']:
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
                step=calibration['threshH']
            continue

        hand0 = handBgst0.bgst(_frame0)
        hand1 = handBgst1.bgst(_frame1)
        hand0 = hand0[crop[0][2]:crop[0][3] , crop[0][0]:crop[0][1]]
        hand1 = hand1[crop[1][2]:crop[1][3] , crop[1][0]:crop[1][1]]

        if step==calibration['threshH']:
            if not mcv.clean(hand0):
                handBgstPara0['sbsThreshH']=handBgstPara0['sbsThreshH']-2
                handBgst0.setThresh(handBgstPara0['sbsThreshL'],handBgstPara0['sbsThreshH'])
                print "sbsThresh "+str(handBgstPara0['sbsThreshH'])+" "+str(handBgstPara1['sbsThreshH'])
            if not mcv.clean(hand1):
                handBgstPara1['sbsThreshH']=handBgstPara1['sbsThreshH']-2
                handBgst1.setThresh(handBgstPara1['sbsThreshL'],handBgstPara1['sbsThreshH'])
                print "sbsThresh "+str(handBgstPara0['sbsThreshH'])+" "+str(handBgstPara1['sbsThreshH'])
            cv2.imshow("frame0",_frame0)
            cv2.imshow("frame1",_frame1)
            cv2.imshow("hand0",hand0)
            cv2.imshow("hand1",hand1)
            k = cv2.waitKey(1)
            if k==27:
                break
            elif k==194: #f5
                handBgstPara0['sbsThreshH']=255
                handBgstPara1['sbsThreshH']=255
                handBgst0.setThresh(handBgstPara0['sbsThreshL'],handBgstPara0['sbsThreshH'])
                handBgst1.setThresh(handBgstPara1['sbsThreshL'],handBgstPara1['sbsThreshH'])
            elif k==195:
                saveConfig(para, depth, handBgstPara0, handBgstPara1, prIdPara0, prIdPara1, user)
                print "[calibration] set threshHigh "+str(handBgstPara0['sbsThreshH'])+" "+str(handBgstPara1['sbsThreshH'])
                step=calibration['yth']
            continue

        preFingers0 = lcid.preIndexUD(hand0,frame0, 300,
                                    step,prIdPara0['Uthresh'],prIdPara0['Dthresh'])
        preFingers1 = lcid.preIndexUD(hand1,frame1, 300,
                                    step,prIdPara1['Uthresh'],prIdPara1['Dthresh'])

        # locating tip
        finThumb0 = (0,0)
        finThumb1 = (0,0)
        if len(preFingers0)==0:
            finIndex0 = pre0
        elif len(preFingers0) ==1:
            finIndex0 = prlc.prlc("notsmooth",cnt = preFingers0[0],img = frame0,textPos=40)
            pre0=finIndex0
        else:
            finThumb0 = prlc.prlc("notsmooth",cnt = preFingers0[0],img = frame0,textPos=20)
            finIndex0 = prlc.prlc("notsmooth",cnt = preFingers0[1],img = frame0,textPos=40)
            if step==calibration['yth']:
                cv2.putText(frame0,str(mcv.ptoint(finIndex0)[0])+" "+str(mcv.ptoint(finIndex0)[1]),(10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
                cv2.putText(frame0,str(mcv.ptoint(finThumb0)[0])+" "+str(mcv.ptoint(finThumb0)[1]),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
                cv2.circle(frame0,mcv.ptoint(finIndex0),2,colors.colors['white'],-1)
                cv2.circle(frame0,mcv.ptoint(finThumb0),2,colors.colors['white'],-1)
            else:
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
            pre1=finIndex1
        else:
            finThumb1 = prlc.prlc("notsmooth",cnt = preFingers1[0],img = frame1, textPos=20)
            finIndex1 = prlc.prlc("notsmooth",cnt = preFingers1[1],img = frame1, textPos=40)
            if step==calibration['yth']:
                cv2.putText(frame1,str(mcv.ptoint(finIndex1)[0])+" "+str(mcv.ptoint(finIndex1)[1]),(10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
                cv2.putText(frame1,str(mcv.ptoint(finThumb1)[0])+" "+str(mcv.ptoint(finThumb1)[1]),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
                cv2.circle(frame1,mcv.ptoint(finIndex1),2,colors.colors['white'],-1)
                cv2.circle(frame1,mcv.ptoint(finThumb1),2,colors.colors['white'],-1)
            if mcv.distance(finIndex0, mcv.subt(finThumb1, dis01)) < mcv.distance(finIndex0, mcv.subt(finIndex1, dis01)): ## dis
                finIndex1 = finThumb1
            if step>=calibration['yth']:
                cv2.circle(frame1,mcv.ptoint(finIndex1),3,colors.colors['yellow'],-1)
            pre1=finIndex1

        if step==calibration['yth']:
            cv2.rectangle(_frame0,(active[0],active[2]),(active[1],active[3]),colors.colors['green'])
            cv2.circle(_frame0,(active[0]+10,active[3]-10), 3, colors.colors['red'])
            cv2.circle(_frame0,(active[1]-10,active[2]+10), 3, colors.colors['green'])
            if setYth:
                prIdPara0['yth']=max(finThumb0[1],prIdPara0['yth'])
            cv2.putText(frame0,str(setYth)+" "+str(prIdPara0['yth']),(10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.imshow("frame0",frame0)
            cv2.imshow("frame1",frame1)
            k=cv2.waitKey(1)
            if k==192:#f3
                setYth = not setYth
            if k==194:#f5
                prIdPara0['yth']=active[2]-crop[0][2]
            if k==195:
                saveConfig(para, depth, handBgstPara0, handBgstPara1, prIdPara0, prIdPara1, user)
                step=calibration['depth']
            if k==27:
                break
            continue

        finIndex0 = [finIndex0[0]+crop[0][0], finIndex0[1]+crop[0][2]]
        finIndex1 = [finIndex1[0]+crop[1][0], finIndex1[1]+crop[1][2]]
        dp.getTouch(finIndex0,finIndex1,preF0,preF1,alpha,dat,depth['l'],depth['h'],depth['thresh'],active)

        if step==calibration['depth']:
            preF0=finIndex0
            preF1=finIndex1
            cv2.circle(_frame0,(int(finIndex0[0]),int(finIndex0[1])),3,colors.colors['yellow'],-1)
            cv2.circle(_frame1,(int(finIndex1[0]),int(finIndex1[1])),3,colors.colors['yellow'],-1)
            cv2.rectangle(_frame0,(active[0],active[2]),(active[1],active[3]),colors.colors['green'])
            cv2.putText(_frame0,str(dat['depth']) + " "+str(dat['absDepth']),(10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.putText(_frame0,str(dat['touch']) + " "+str(depth['thresh']),(10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.putText(_frame0,str(dat['position'][0])+" "+str(dat['position'][1]),(10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
            cv2.imshow("frame0",_frame0)
            cv2.imshow("frame1",_frame1)
            k = cv2.waitKey(1)
            if k==27:
                break
            elif k==61: #+
                depth['thresh']+=0.05
            elif k==45:#-
                depth['thresh']-=0.05
            elif k==195:
                saveConfig(para, depth, handBgstPara0, handBgstPara1, prIdPara0, prIdPara1, user)
            continue

        if dat['touch'] and dat['pointing'] and step==calibration['final']:
            if mode==0: # absolute
                dat['position'][0]=finIndex0[0]
                dat['position'][1]=finIndex0[1]
                dat['position'][0]= (active[1]-dat['position'][0]+0.0) *width / activeShape[0]
                dat['position'][1]= (active[3]-dat['position'][1]+0.0) *height/ activeShape[1]
                mouse.move(dat['position'][0],dat['position'][1])

            if mode==1: # relative
                delta = list(mcv.subt( preF0,finIndex0 ))
                delta[0]=delta[0]*(width+0.0)/activeShape[0]/relaScale
                delta[1]=delta[1]*(height+0.0)/activeShape[1]/relaScale
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

    handBgstPara0['sbsThreshL']=handBgstPara0['sbsThreshL']
    handBgstPara1['sbsThreshL']=handBgstPara1['sbsThreshL']
    handBgstPara0['sbsThreshH']=handBgstPara0['sbsThreshH']
    handBgstPara1['sbsThreshH']=handBgstPara1['sbsThreshH']
    prIdPara0['yth']=prIdPara0['yth']
    saveConfig(para,depth,handBgstPara0,handBgstPara1,prIdPara0,prIdPara1,user)
    fps.stop()
    print("[TEST1] elasped time: {:.2f}".format(fps.elapsed()))
    print("[TEST1] approx. FPS: {:.2f}".format(fps.fps()))

    kill['kill'] = True
    cap0.release()
    cap1.release()
    cv2.destroyAllWindows()

import os
import shutil

def saveConfig(para,depth,handBgstPara0,handBgstPara1,prIdPara0,prIdPara1,user):
    with open("./configuration/"+user+".json", 'w') as f:
        js = {'ctrl':para,
              'depth':depth,
              'hand':[handBgstPara0,handBgstPara1],
              'lc':[prIdPara0,prIdPara1]}
        json.dump(js,f)
        print("write to file")

def initializeUser(user):
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
    initializeUser(args['user'])

    global calibration
    calibrationIndexes = ['position','gain','threshL0','threshL1','getBg','threshH','yth','plane','depth','final']
    calibration = {}
    for i in xrange(len(calibrationIndexes)):
        calibration[calibrationIndexes[i]] = i

    # variables for multi-processing
    manager = Manager()
    key = manager.dict() # get keyboard events
    kill = manager.dict() # killing other processes or not

    key['status']=False
    key['info']=""

    kill['kill']=False

    if args['step']=='final':
        p = Process(target=keylogger.log, args=(key,kill))
        p.start()

    global timers
    timers = [Timer() for i in xrange(4)]
    mainLoop(calibration[args['step']], kill, key, args['user'], args['mode'])
