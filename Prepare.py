'''
Created on Aug 17, 2017
@author: qian
'''
import cv2
import colors
import numpy as np
import json
# set arguments
import argparse

def adjust():
    record = False
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out0 = 0
    out1 = 0
    while True:
        ret, f0 = cap0.read()
        ret, f1 = cap1.read()
        if not ret:
            break
        frame0 = f0.copy()
        frame1 = f1.copy()
        # adjust the position 0,1-vertical 2,3-horizontal
        cv2.line(frame0,(para['crop'][0][0],para['crop'][0][2]),(para['crop'][0][0],para['crop'][0][3]),colors.colors['pink'],2)
        cv2.line(frame0,(para['crop'][0][1],para['crop'][0][2]),(para['crop'][0][1],para['crop'][0][3]),colors.colors['pink'],2)
        cv2.line(frame0,(para['crop'][0][0],para['crop'][0][2]),(para['crop'][0][1],para['crop'][0][2]),colors.colors['pink'],2)
        cv2.line(frame0,(para['crop'][0][0],para['crop'][0][3]),(para['crop'][0][1],para['crop'][0][3]),colors.colors['pink'],2)
        # 
        cv2.line(frame1,(para['crop'][1][0],para['crop'][1][2]),(para['crop'][1][0],para['crop'][1][3]),colors.colors['pink'],2)
        cv2.line(frame1,(para['crop'][1][1],para['crop'][1][2]),(para['crop'][1][1],para['crop'][1][3]),colors.colors['pink'],2)
        cv2.line(frame1,(para['crop'][1][0],para['crop'][1][2]),(para['crop'][1][1],para['crop'][1][2]),colors.colors['pink'],2)
        cv2.line(frame1,(para['crop'][1][0],para['crop'][1][3]),(para['crop'][1][1],para['crop'][1][3]),colors.colors['pink'],2)
        # 
        cv2.line(frame0,(para['active1'][0],para['active1'][2]),(para['active1'][0],para['active1'][3]),colors.colors['green'],2)
        cv2.line(frame0,(para['active1'][1],para['active1'][2]),(para['active1'][1],para['active1'][3]),colors.colors['green'],2)
        cv2.line(frame0,(para['active1'][0],para['active1'][2]),(para['active1'][1],para['active1'][2]),colors.colors['green'],2)
        cv2.line(frame0,(para['active1'][0],para['active1'][3]),(para['active1'][1],para['active1'][3]),colors.colors['green'],2)
        cv2.putText(frame1,'Press Space to start/end recording',(10,20), font, 0.5,(255,255,255),1,cv2.LINE_AA)

        if record:
            out0.write(f0)
            out1.write(f1)
            cv2.putText(frame1,'Recording...',(10,40), font, 0.5,(255,255,255),1,cv2.LINE_AA)
        cv2.imshow('0',frame0)
        cv2.imshow('1',frame1)
        k = cv2.waitKey(1)
        if k == ord('c'):
            cv2.imwrite('hand0.png',f0)
            cv2.imwrite('hand1.png',f1)
        if k == 32:
            if record:
                record = False
                out0.release()
                out1.release()
            else:
                record = True
                out0 = cv2.VideoWriter(para['root']+para['vname']+"0.avi", fourcc,para['fps'],(para['w'],para['h']))
                out1 = cv2.VideoWriter(para['root']+para['vname']+"1.avi", fourcc,para['fps'],(para['w'],para['h']))
        if k == 27:
            break    

def draw_rec(event, x, y, flags, param):
    global gx,gy,activeWindow,collect
    if event == cv2.EVENT_MOUSEMOVE:
        gx = x
        gy = y
        activeWindow = param
    if event == cv2.EVENT_LBUTTONUP:
        collect=True
    
def capture():
    global gx,gy,activeWindow,collect,roi
    cv2.namedWindow('0')
    cv2.setMouseCallback('0', draw_rec, "0")
    cv2.namedWindow('1')
    cv2.setMouseCallback('1', draw_rec, "1")
    count = 0
    strr = "Click to sample"
    while True:
        ret, frame0 = cap0.read()
        ret, frame1 = cap1.read()
        if not ret:
            break
        nx = gx-para['sample-size']
        ny = gy-para['sample-size']
        if activeWindow=="0":
            cv2.rectangle(frame0,(nx-1,ny-1),(gx+1,gy+1),(0,255,0),1)
            cv2.putText(frame0,strr,(10,20), font, 0.5,(255,255,255),1,cv2.LINE_AA)
            if collect:
                count+=1
                strr='samples: '+str(count)
                if len(roi)==0:
                    roi=frame0[ ny:gy,nx:gx]
                else:
                    roi=np.vstack( (roi,frame0[ ny:gy,nx:gx]) )
                collect=False
        elif activeWindow=="1":
            cv2.rectangle(frame1,(nx-1,ny-1),(gx+1,gy+1),(0,255,0),1)
            cv2.putText(frame1,strr,(10,20), font, 0.5,(255,255,255),1,cv2.LINE_AA)
            if collect:
                count+=1
                strr='samples: '+str(count)
                if len(roi)==0:
                    roi=frame1[ ny:gy,nx:gx]
                else:
                    roi=np.vstack( (roi,frame1[ ny:gy,nx:gx]) )
                collect=False
        cv2.imshow('0',frame0)
        cv2.imshow('1',frame1)
        k = cv2.waitKey(1)
        if k == ord('h'):
            cv2.imwrite(para['root']+"hand"+activeWindow+".png",roi)
            roi=[]
            count = 0
            strr= "save to hand "+activeWindow
        elif k == ord('n'):
            cv2.imwrite(para['root']+"nail"+activeWindow+".png",roi)
            roi=[]
            count = 0
            strr = "save to nail "+activeWindow
        elif k == 27:
            break    

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", type=str, default="./config/wei.json",
    help="Which config file to load")
args = vars(ap.parse_args())

# load config
with open(args['config']) as json_data_file:
    data = json.load(json_data_file)
    para = data['ctrl']
cap0 = cv2.VideoCapture(0)
cap1 = cv2.VideoCapture(1)
w=320
h=240
fps=200
gain=0.5
cap0.set(cv2.CAP_PROP_FRAME_WIDTH, w);
cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, h);
cap0.set(cv2.CAP_PROP_FPS, fps)
cap0.set(cv2.CAP_PROP_GAIN,gain)
cap1.set(cv2.CAP_PROP_FRAME_WIDTH, w);
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, h);
cap1.set(cv2.CAP_PROP_FPS, fps)
cap1.set(cv2.CAP_PROP_GAIN,gain)
cv2.namedWindow('0', cv2.WINDOW_NORMAL)
cv2.namedWindow('1', cv2.WINDOW_NORMAL)
font = cv2.FONT_HERSHEY_SIMPLEX

adjust()
# sample
gx = 0
gy = 0
roi=[]
activeWindow=""
collect=False
capture()

cap0.release()
cap1.release()
cv2.destroyAllWindows()
    
