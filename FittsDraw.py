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
import FittsIO
import FittsIni as ini
def init(x,y):
    global canvasMiddlex, canvasMiddley
    canvasMiddlex=x
    canvasMiddley=y
    
def drawStartScreen(canvas):
    canvas.create_text(canvasMiddlex, canvasMiddley-120, text="enter your name then press [Enter]:", font="Helvetica 20",fill="#556b2f")
    if canvas.data.STATE=="start":
        if canvas.data.timerCounter%4<2:
            canvas.create_text(canvasMiddlex, canvasMiddley,text=""+canvas.data.name,font="Helvetica 25")
        else:
            canvas.create_text(canvasMiddlex, canvasMiddley,text=""+canvas.data.name+"_",font="Helvetica 25")
    else: 
        canvas.create_text(canvasMiddlex, canvasMiddley,text=""+canvas.data.name,font="Helvetica 25")
    
    canvas.create_text(canvasMiddlex, canvasMiddley+180, text="[Click] to choose device", font="Helvetica 20", fill="#556b2f")
    drawDeviceOptions(canvas)
    canvas.create_text(canvasMiddlex, canvasMiddley+500, text="press [S] to start", font="Helvetica 20", fill="#556b2f")
#
def drawDeviceOptions(canvas):
    y = canvasMiddley+330
    x = canvasMiddlex-600
    rec = 30
    word = 100
    canvas.create_rectangle(x-rec,y-rec,x+rec,y+rec, fill=canvas.data.circleMouse) #mouse    
    canvas.create_text(x+word,y, text="mouse", font="Helvetica 25", anchor="w" )
    canvas.create_rectangle(x-rec+450,y-rec,x+rec+450,y+rec, fill=canvas.data.trackpad) #mouse    
    canvas.create_text(x+word+450,y, text="trackpad", font="Helvetica 25", anchor="w" )
    canvas.create_rectangle(x-rec+1000,y-rec,x+rec+1000,y+rec, fill=canvas.data.fingers) #mouse    
    canvas.create_text(x+word+1000,y, text="fingers", font="Helvetica 25", anchor="w" )
#
def drawCircles(canvas):
    angle=(math.pi/2)-math.pi*(canvas.data.clicks)/(canvas.data.numberToGo)
    cX=(canvas.data.width /2)+(canvas.data.diameter/2)*math.cos(angle)*((-1)**canvas.data.clicks)
    cY=(canvas.data.height/2)-(canvas.data.diameter/2)*math.sin(angle)*((-1)**canvas.data.clicks)
    canvas.data.centerX=cX
    canvas.data.centerY=cY
    x1=cX-canvas.data.circleWidth/2
    y1=cY-canvas.data.circleWidth/2
    x2=cX+canvas.data.circleWidth/2
    y2=cY+canvas.data.circleWidth/2
    canvas.create_oval(x1,y1,x2,y2, fill="#556b2f", outline="#556b2f")
#
def drawError(canvas):
    for i in xrange(len(canvas.data.allError)):
        cX=canvas.data.allError[i][0]
        cY=canvas.data.allError[i][1]
        x1=cX-2
        y1=cY-2
        x2=cX+2
        y2=cY+2
        canvas.create_oval(x1,y1,x2,y2, fill="red")

def drawTyping(canvas):
    canvas.data.currentWord = canvas.data.wordList[canvas.data.random]
    canvas.create_text(canvasMiddlex-100, canvasMiddley, \
        text = canvas.data.wordList[canvas.data.random], \
        font="Helvetica 30", fill="#556b2f", anchor="w")
    canvas.create_text(canvasMiddlex-100, canvasMiddley+100, \
        text = canvas.data.typed, font="Helvetica 30",\
        fill="#666666", anchor="w")
    canvas.create_text(canvasMiddlex-100, canvasMiddley+100, \
        text = ''.join(['_' for i in xrange(len(canvas.data.currentWord)-1)]), font="Helvetica 30",\
        fill="#666666", anchor="w")
#
def drawTime(canvas):
    canvas.create_rectangle(100,100,400,200, fill="white", outline="white")
    canvas.create_text(150,150, text = str(time.time()), font="Helvetica 10",\
        fill="#666666", anchor="w")
    
def drawKSI(canvas,on):
    if on:
        canvas.create_text(150,150, text = "Pointing", font="Helvetica 30",\
        fill="#DC143C", anchor="w")
    else:
        canvas.create_text(150,150, text = "Typing", font="Helvetica 30",\
        fill="#cccccc", anchor="w")
        
def drawProgress(canvas):
    canvas.create_text(canvasMiddlex+1500,150, text = "Section "+str(canvas.data.round+1)+"/"+str(canvas.data.numberOfRounds), font="Helvetica 15",\
    fill="black", anchor="w")
    canvas.create_text(canvasMiddlex+1500,220, text = "Task "+str(canvas.data.clicks+canvas.data.numberToGo*canvas.data.section)+"/"+str(canvas.data.numberToGo*canvas.data.numberOfSections), font="Helvetica 15",\
    fill="black", anchor="w")
    
def redrawAll(canvas):   # DK: redrawAll() --> redrawAll(canvas)
    global canvasMiddlex, canvasMiddley
    canvas.delete(ALL)
    if canvas.data.device=="fingers":
        drawKSI(canvas,canvas.data.KSI)
    if canvas.data.STATE == "start" or canvas.data.STATE == "Name_Set": #draw start screen
        drawStartScreen(canvas)
    elif (canvas.data.STATE == "Display_Target" or canvas.data.STATE == "Pointing_Target"):
        drawCircles(canvas)
        drawError(canvas)
        drawProgress(canvas)
    elif (canvas.data.STATE == "Display_Word" or canvas.data.STATE == "Typing_Word" or canvas.data.STATE == "Ready_to_type" or canvas.data.STATE == "Switching_Word"):
        drawTyping(canvas)
        drawProgress(canvas)
    elif canvas.data.STATE == "Section_End":
        canvas.create_text(canvasMiddlex, canvasMiddley, text="section "+str(canvas.data.round)+" completed", font="Helvetica 25")
        canvas.create_text(canvasMiddlex, canvasMiddley+100, text="press [space] to continue", font="Helvetica 25")
    elif canvas.data.STATE == "Study_End":
        canvas.create_text(canvas.data.width/2, canvasMiddley, text="testing completed", font="Helvetica 25")
