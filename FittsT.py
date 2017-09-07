'''
Created on Sep 1, 2017

@author: qian
'''
import FittsDraw as draw
import FittsIni as ini
import FittsIO as io
import math
import time
import string
import random

def resetPath(canvas):
    canvas.data.trajectories.append(canvas.data.path)
    canvas.data.allPathTimes.append(canvas.data.pathTimes)
    canvas.data.path=[]
    canvas.data.pathTimes=[]
    #Determine which word to type
    canvas.data.random = random.randint(0,len(canvas.data.wordList)-1)

#check if any errors in clicking
def checkClicked(x,canvas):
    for i in xrange(len(canvas.data.error)):
        if canvas.data.error[i]==x:
            return "1"
    return "0"

def mousePressed(canvas, event,x,y):
    if (canvas.data.STATE == "Display_Target" or
            canvas.data.STATE == "Pointing_Target"):
        #on the first click, record the location
        if canvas.data.errorMade == 0:
            canvas.data.listX.append(event.x)
            canvas.data.listY.append(event.y)
            canvas.data.listcX.append(canvas.data.centerX)
            canvas.data.listcY.append(canvas.data.centerY)
        # If correct click,
        if (((event.x-canvas.data.centerX)**2) +
                ((event.y-canvas.data.centerY)**2) <
                ((canvas.data.circleWidth/2)**2)):
            successfulClick(canvas, event)
        else:  # clicked outside of the circle
            missedClick(canvas, event)
    elif canvas.data.STATE == "start" or canvas.data.STATE == "Name_Set":
        #so this is for the start screen, when choosing devices
        mouseButtonPressed(canvas, event,x,y)
    draw.redrawAll(canvas)
#     draw.drawTime(canvas)

def successfulClick(canvas, event):
    if (not canvas.data.errorMade): #make it so that it only checks the first error. ie multiple errors don't matter
        canvas.data.errorMargin.append(0)
    canvas.data.errorClicks=[]
    canvas.data.allError=[]
    canvas.data.errorMade=0
    #this time.time is to ignore the time to press keys:
    if canvas.data.clicks<canvas.data.numberToGo:
        canvas.data.STATE = "Display_Word"
    canvas.data.clicks+=1
    canvas.data.movingTimes.append(time.time()-canvas.data.movingTime)
    canvas.data.buttonTime=time.time()
    resetPath(canvas)

def missedClick(canvas, event):
    errorX=event.x-canvas.data.centerX
    errorY=event.y-canvas.data.centerY
    value=(errorX**2)+(errorY**2)
    errorDel= math.sqrt(value)-(canvas.data.circleWidth/2)

    canvas.data.allError.append([event.x,event.y])
    if (not canvas.data.errorMade): #make it so that it only checks the first error. ie multiple errors don't matter
        canvas.data.errorMargin.append(errorDel)
        canvas.data.errorClicks.append([event.x,event.y])
        canvas.data.errorMade = 1

def mouseButtonPressed(canvas, event, canvasMiddlex, canvasMiddley):
    y = canvasMiddley+330
    x = canvasMiddlex-600
    rec = 30
    if ((x-rec)<=event.x<=(x+rec) and (y-rec)<=event.y<=(y+rec)):
        canvas.data.circleMouse="#556b2f"
        canvas.data.trackpad=None 
        canvas.data.fingers=None
    if ((x-rec+450)<=event.x<=(x+rec+450) and (y-rec)<=event.y<=(y+rec)):
        canvas.data.circleMouse=None
        canvas.data.trackpad="#556b2f" 
        canvas.data.fingers=None
    if ((x-rec+1000)<=event.x<=(x+rec+1000) and (y-rec)<=event.y<=(y+rec)):
        canvas.data.circleMouse=None
        canvas.data.trackpad=None 
        canvas.data.fingers="#556b2f"

############################ key
def keyPressed(canvas, event):
    #While actual testing.
    if (canvas.data.STATE == "Name_Set" and event.keysym=="s"):
        canvas.data.start=True
        ini.setDeviceName(canvas)
        ini.startClock(canvas)
        io.createDirectory(canvas)
        io.writeFHead(canvas)
        canvas.data.STATE = "Display_Target"
    #Below is for set up
    elif canvas.data.STATE == "start":
        ini.setUserName(canvas,event)
    elif canvas.data.STATE == "Display_Word":
        canvas.data.buttonTimes.append(time.time()-canvas.data.buttonTime)
        if canvas.data.device=="mouse" or canvas.data.device=="trackpad":
            canvas.data.STATE = "Ready_to_type"
            keyTyping(canvas,event)
        elif event.keysym=="Tab":
            canvas.data.STATE = "Ready_to_type"
        else:
            canvas.data.STATE = "Switching_Word"
    elif canvas.data.STATE == "Switching_Word":
        if event.keysym=="Tab":
            canvas.data.STATE = "Ready_to_type"
    elif canvas.data.STATE == "Typing_Word" or canvas.data.STATE =="Ready_to_type":
        keyTyping(canvas,event)     
    elif canvas.data.STATE == "Display_Target" or canvas.data.STATE == "Pointing_Target":
#         print event.keysym
        if event.keysym!="space" and event.keysym!="Tab":
            canvas.data.keyPressed[canvas.data.clicks]="1"
    elif (canvas.data.STATE == "Section_End" and event.keysym=="space"):
        canvas.data.STATE = "Display_Target"
        ini.startClock(canvas)
    if event.keysym == "Tab":
        canvas.data.KSI = not canvas.data.KSI
    draw.redrawAll(canvas)
#     draw.drawTime(canvas)

def keyTyping(canvas,event):
    if canvas.data.STATE == "Ready_to_type":
        canvas.data.STATE = "Typing_Word"
        #should account for typingtime as well
        canvas.data.typingTime=time.time()
    #append the text entry
    if event.keysym in string.ascii_letters:
        canvas.data.typed = "".join((canvas.data.typed, event.keysym))
    elif event.keysym=="BackSpace":
        canvas.data.typed=canvas.data.typed[:-1]
    #check if correct word
    if canvas.data.typed == canvas.data.currentWord:
        canvas.data.typingTimes.append(time.time()-canvas.data.typingTime)
        canvas.data.time+=(time.time()-canvas.data.typingTime)
        canvas.data.typed = ""
        canvas.data.listOfWords.append(canvas.data.currentWord)
        if canvas.data.clicks<canvas.data.numberToGo:
            canvas.data.STATE = "Display_Target"
            canvas.data.homingTime = time.time()
        else:
            canvas.data.STATE = "Display_Target"
            io.writeFiles(canvas)
            # io.writeTracking(canvas)
            canvas.data.section +=1
            if canvas.data.section ==canvas.data.numberOfSections:
                canvas.data.section = 0
                canvas.data.round += 1
                canvas.data.STATE = "Section_End"
            if (canvas.data.round==canvas.data.numberOfRounds):
                canvas.data.STATE = "Study_End"
            else:
                ini.setSecondaryValues(canvas)
            canvas.data.homingTime = time.time()

####### motion
def motion(canvas, event): #store in a list and then delete lk half
        #Start moving time measurement
#     draw.drawTime(canvas)
    if canvas.data.STATE == "Pointing_Target" or canvas.data.STATE == "Display_Target":
        x, y, state = event.x, event.y, canvas.data.STATE
        canvas.data.path.append([x,y,state])
        elapsed=time.time()-canvas.data.time
        canvas.data.pathTimes.append(elapsed)
    if canvas.data.STATE == "Display_Target":
        canvas.data.homingTimes.append(time.time()-canvas.data.homingTime)
        canvas.data.movingTime = time.time()
        canvas.data.STATE = "Pointing_Target"
