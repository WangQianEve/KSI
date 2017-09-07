# KSI User Study Procedure
Say hello and remind people DO NOT move the laptop and the cameras.

## Explanation of the study
The goal of this study is to evaluate the performance of different devices for pointing tasks, that is touchpad, mouse and a device we developed called indexSense. It uses two cameras to track your index finger.

## Consent form
In this study you will be clicking at targets that are going to appear on the screen. You will also be typing simple words in between the pointing tasks. This is explained in this consent form, if you want you can read it, once you finish you can sign here.

## Calibration Instructions
This is IndexSense, it will be tracking your index finger and with it you can control the pointer of the mouse, though only if you touch the keyboard.

Now before you can use indexSense, first we need to calibrate device for you.

ask how will they do.

### position
+ run "python autoCali.py -u [username] -s position"
+ check if the pink rectangles are the same area.
+ place the mouse pad to cover both pink rec.

now please put your right hand on the mouse pad, make it appear in the pink rectangle and keep still.

+ *press f6 to set gain, or esc to exit*

### gain
+ *press f6 to continue*

### thresh low
now I need you to keep your fingers touching the pad, rest your wrist on the pad also and spread the thumb, index and middle finger like this, and make them appear in the middle of this image.

now slowly bend you index finger as if you are dragging the cursor to the bottom right corner. OK now please keep your wrist still, and rotate your whole hand anticlockwise, and clockwise.

OK, now I need you to that again. Spread, drag, and rotate.

+ *press f5 to reset, f6 to continue with the other camera*
+ *take away the hand and mouse pad*

### get bg
*press f3 to set Bg first, then f6 to continue*

### thresh high
*when the output is stable press f6*

### yth
now rest both of your hands on the keyboard at the position when you type.

so this is the sensing area, it is from from key XX to key XXX.(green box on the screen). I need you to remember that, because this image will not show when you control the cursor.

+ using indexSense we hope you to separate the thumb, index and middle finger clearly. Especially when you touch the lower area of the green rectangle.

can you type "university" first and then move as if your are dragging the cursor from the green point to the red point, with your wrist rest on the laptop.

Stop at the red point.

now move your index from red to green and stop at green.

*if they place the thumb too high, tell them not to.*

*press f5 to reset, f6 to continue, f3 to start setting*

### depth
now please only use your index and thumb finger like this, still rest your wrist on the laptop, and keep touching the keyboard and moves your index finger slowly from up to down, but inside the green rectangle.

### guide
now you can practice using it a little bit. The yellow point is where the indexSense is tracking. When you practice I hope you :
1. get familiar with the area.
2. don't lift you whole hand up, just try to be comfortable, we encourage you rest other fingers on the keyboard as well because it's comfortable. Unless you always do this when you are typing.
3. to better control the cursor don't make index too close to any other finger.
4. don't put your thumb too high.
Now you can start practicing.

## Demographics and discomfort test

## Deactivate accel
python disAccel.py -c mouse/indexS/touchpad

and manually turn off touchpad

## Fitts law test
+ run Fitts.py -u 0 -r 0 with username testxxx

### about indexSense
+ tab to turn on/off
+ spacebar to click (left thumb)
+ do not press escape key

### Fitts law test
In this test you are going to click on the targets that appear on screen. You have to try to be as fast and accurate as possible. After you click correctly, you'll see a word on the screen, you don't need to move the cursor to the input area, just turn off the indexSense and start typing. You need to type the word correctly.

You are going to be testing 3 devices and between evaluations there is going to be a 5 minutes resting period. For each device there are 8 sections, and it takes around 20 minutes to finish them, so it's around 1 hour in total. But it depends on your speed.

Now you can start practicing, when you think you are familiar with it, let me know and we'll start the study.

## Qualitative evaluation & feedback

## Pay
