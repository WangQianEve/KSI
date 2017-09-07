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
import FittsDraw as draw
import FittsT

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("-u", "--user", type=int, default=1,
    help="Which config file to load")
ap.add_argument("-r", "--round", type=int, default=0,
    help="Which step")
ap.add_argument("-s", "--section", type=int, default=0,
    help="Which step")
args = vars(ap.parse_args())

def timerFired(canvas):
    draw.redrawAll(canvas)
    canvas.data.timerCounter += 1
    delay = 250 # milliseconds
    def f():
        timerFired(canvas) # DK: define local fn in closure
    canvas.after(delay, f) # pause, then call timerFired again

def init(canvas):
    canvas.data.numberToGo = 12  # number of clicks to do
    canvas.data.numberOfSections = 3
    canvas.data.numberOfRounds = 8
    ini.setInitialValues(canvas,args['user'],args['round'],args['section'])  # doesn't change through
    ini.setSecondaryValues(canvas)  # changes per round
    draw.init(canvasMiddlex, canvasMiddley)
    canvas.data.random = random.randint(0, len(canvas.data.wordList)-1)

def run():
    # create the root and the canvas
    root = Tk()
    cHeight = 2160
    cWidth = 3840
    global canvasMiddlex , canvasMiddley
    canvasMiddlex = cWidth/2 - 200
    canvasMiddley = cHeight/2 - 400
    canvas = Canvas(root, width=cWidth, height=cHeight, bg="#f5f5f5")
    canvas.pack()

    class Struct:
        pass
    canvas.data = Struct()
    canvas.data.width = cWidth
    canvas.data.height = cHeight
    init(canvas)
    root.bind("<Button-1>", lambda event: FittsT.mousePressed(canvas, event,canvasMiddlex,canvasMiddley))
    root.bind("<Key>", lambda event:  FittsT.keyPressed(canvas, event))
    root.bind("<Motion>", lambda event: FittsT.motion(canvas, event))
    timerFired(canvas)
    root.mainloop()

run()
