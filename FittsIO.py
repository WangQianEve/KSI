'''
Created on Sep 1, 2017

@author: qian
'''
from Tkinter import *
import math
import time
import string
import datetime
import tkFileDialog
import os.path
import random
import FittsIni as ini
import FittsT

def createDirectory(canvas):
    path="./userDataMFLT/"
    savedTitle=canvas.data.name
    i=0
    value=True
    while value:
        if (i==0):
            if not os.path.exists(path+savedTitle):
                os.makedirs(path+savedTitle)
                value=False
            else:
                i+=1
        else:
            if not os.path.exists(path+savedTitle+str(i)):
                os.makedirs(path+savedTitle+str(i))
                value=False
            else:
                i+=1
    if i==0:
        canvas.data.directoryPath=path+savedTitle+"/"
        canvas.data.directoryPath=canvas.data.directoryPath.rstrip('\n')

    else:
        canvas.data.directoryPath=path+savedTitle+str(i)+"/"
        canvas.data.directoryPath=canvas.data.directoryPath.rstrip('\n')

def writeFHead(canvas):
    path=canvas.data.directoryPath
    savedTitle=path+str(canvas.data.name)+str(canvas.data.device)+".csv"
    f=open(savedTitle, 'w')
    f.write("Target#, time, targetX, targetY, clickX, clickY, clicked, keyPressed, width, errorMargin, Homing Time1, Keyboard Homingtime, Typingtime, Word, round, condition set, condition\n")
    f.close()
    # savedTitle=path+str(canvas.data.name)+str(canvas.data.device)+"MFLTtracking"+".csv"
    # f=open(savedTitle, 'w')
    # f.write("Target#, times, x, y \n")

def writeFiles(canvas):
    path=canvas.data.directoryPath
    savedTitle=path+str(canvas.data.name)+str(canvas.data.device)+".csv"
    f=open(savedTitle, 'a')
    for x in xrange(canvas.data.numberToGo):
        clicked="0" if canvas.data.errorMargin[x]==0 else "1"
        stuff = str(x) + "," +('%.3f'%(canvas.data.movingTimes[x]))+ "," +  ('%.3f'%(canvas.data.listcX[x])) +"," + ('%.3f'%(canvas.data.listcY[x])) +"," +\
            ('%.3f'%(canvas.data.listX[x])) +"," + ('%.3f'%(canvas.data.listY[x])) +","  + clicked+","+canvas.data.keyPressed[x]+","+ \
            str(canvas.data.circleWidths[canvas.data.configuration]) +"," +  \
            ('%.3f'%(canvas.data.errorMargin[x])) +"," + ('%.3f'%(canvas.data.homingTimes[x]))+"," + \
            ('%.3f'%(canvas.data.buttonTimes[x])) +"," + ('%.3f'%(canvas.data.typingTimes[x]))+ ","+str(canvas.data.listOfWords[x])+ "," + \
            str(canvas.data.round)+","+ canvas.data.configurations[canvas.data.round]+","+ canvas.data.configuration+ "\n"
        f.write(stuff)
    f.close()

def readConditions(canvas,userId, cRound):
    f = open("./conditions/conditions.csv",'r')
    for i in xrange(userId):
        line = f.readline()
    f.close()
    return line.split(',')[canvas.data.numberOfRounds*cRound:canvas.data.numberOfRounds*(cRound+1)]

def writeTracking(canvas):
    path=canvas.data.directoryPath
    savedTitle=path+str(canvas.data.name)+str(canvas.data.device)+str(canvas.data.configuration)+"MFLTtracking"+".csv"
    f=open(savedTitle, 'w')
    date = str(datetime.date.today())
    f.write(canvas.data.name+","+str(canvas.data.configuration)+","+date+"\n")
    f.write("Target#, times, x, y \n")
    for x in xrange(canvas.data.numberToGo): #this x is wrt to clicks
        stuff=""
        timesForThisRound=canvas.data.allPathTimes[x] #1d list of [time1, time2, time3....]
        trajectory=canvas.data.trajectories[x] #1d list of (x,y)
        for i in xrange(len(trajectory)):
            stuff=str(timesForThisRound[i]) #time 
            stuff=stuff+","+str(trajectory[i][0]) #x coordinate
            stuff=stuff+","+str(trajectory[i][1]) #y coordinate

            stuff=stuff+","+str(trajectory[i][2]) #State
        
            thing=str(x)+", "+str(stuff)+"\n"
            f.write(thing)
