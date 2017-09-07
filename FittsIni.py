'''
Created on Sep 1, 2017

@author: qian
'''
import string
import time
#
import FittsIO as io
def startClock(canvas):
    canvas.data.time = time.time()
    canvas.data.homingTime = time.time()

def setDeviceName(canvas):
    if canvas.data.circleMouse:
        canvas.data.device="mouse"
    elif canvas.data.trackpad:
        canvas.data.device="trackpad"
    elif canvas.data.fingers:
        canvas.data.device="fingers"
    canvas.data.KSI = True
#
def setUserName(canvas,event):
    if event.keysym in string.ascii_letters or event.keysym in string.digits:
        canvas.data.name=canvas.data.name+event.keysym
    elif event.keysym=="space":
        canvas.data.name=canvas.data.name+" "
    elif event.keysym=="BackSpace":
        canvas.data.name=canvas.data.name[:-1]
    elif event.keysym=="Return":
        canvas.data.STATE = "Name_Set"

def openFile(canvas,tkFileDialog):
    file_path = tkFileDialog.askopenfilename()
    canvas.data.condition = file_path
    readFile(canvas)

def readFile(canvas):
    with open(canvas.data.condition) as f:
        for x in xrange(canvas.data.numberOfRounds):
            canvas.data.configurations.append( str(f.readline()).rstrip() )
            if canvas.data.configurations[-1] == "":
                break
            f.readline()
            canvas.data.circleWidths.append( 2*int(f.readline()) )
            f.readline()
            canvas.data.diameters.append( 2*int(f.readline()) )

def setInitialValues(canvas,userId,cRound,cSection):
    canvas.data.configurations= io.readConditions(canvas,userId,cRound)
    canvas.data.circleWidths={"A":114,"B":54,"C":26}
    canvas.data.diameter = 800
    canvas.data.STATE = "start"
    canvas.data.section = 0
    canvas.data.round = cSection
    
    canvas.data.fStatus = 0
    canvas.data.name = ""
    canvas.data.device = ""
    canvas.data.circleMouse = None
    canvas.data.trackpad = None
    canvas.data.fingers = None
    canvas.data.path = ""
    canvas.data.wordList = [
        'candle',
        'ceiling',
        'lamp',
        'table',
        'computer',
        'chair',
        'door',
        'friend',
        'yahoo',
        'apple',
        'google',
        'him',
        'her',
        'you',
        'bring',
        'kettle',
        'backpack',
        'melon',
        'carnegie',
        'pittsburgh',
        'speakers',
        'microphone',
        'mouse',
        'fingers',
        'keyboard',
        'tissue',
        'towel',
        'paper',
        'printer',
        'scanner',
        'flower',
        'university',
        'college',
        'toothpaste',
        'garbage',
        'suitcase',
        'napkin',
        'restaurant',
        'cafe',
        'gates',
        'center',
        'avenue',
        'street',
        'government',
        'research',
        'sheets',
        'male',
        'female',
        'woods',
        'tree']

    canvas.data.timerCounter = 0
    canvas.data.start = False  # set not to start until name is entered
    canvas.data.typed = ""
    canvas.data.currentWord = ""

def setSecondaryValues(canvas):  # for setting values that are reset every round
    canvas.data.configuration= canvas.data.configurations[canvas.data.round][canvas.data.section]
    canvas.data.circleWidth= canvas.data.circleWidths[canvas.data.configuration]
    
    canvas.data.allPathTimes=[]
    canvas.data.trajectories=[]
    canvas.data.path = []  # 1d array of a single path.
    canvas.data.pathTimes = []

    canvas.data.clicks = 0  # how many I've successfully clicked
    canvas.data.keyPressed = ["0" for i in xrange(canvas.data.numberToGo)]

    canvas.data.errorMargin = []
    canvas.data.errorClicks = []
    canvas.data.errorMade = 0
    # reset when new round
    canvas.data.homingTime = 0
    canvas.data.homingTimes = []
    canvas.data.buttonTime = 0 # successful time
    canvas.data.buttonTimes = []
    canvas.data.typingTime = 0
    canvas.data.typingTimes = []
    canvas.data.movingTime = 0
    canvas.data.movingTimes = []

    canvas.data.listOfWords = []
    canvas.data.allError = []
    canvas.data.listcX = []  # list of X coord of the circle center
    canvas.data.listcY = []  # list of Y coord of the circle center

    canvas.data.listX = []  # list of where user clicked X coord
    canvas.data.listY = []  # list of where user clicked Y coord
