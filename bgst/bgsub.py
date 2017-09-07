import numpy as np
import cv2
import time
cap = cv2.VideoCapture(1)

#cap.set(cv2.CAP_PROP_AUTOFOCUS, 0) # turn the autofocus off
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320);
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240);
cap.set(cv2.CAP_PROP_FPS, 200)
cap.set(cv2.CAP_PROP_GAIN, 0.4)

time.sleep(1)
ret, still = cap.read()
gray_still = cv2.cvtColor(still, cv2.COLOR_BGR2GRAY)
#blur = cv2.bilateralFilter(gray_still, 9, 75, 75)
thresh = cv2.threshold(gray_still, 60, 255, cv2.THRESH_BINARY)[1]
time.sleep(3)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#    blur2 = cv2.bilateralFilter(gray2, 9, 75, 75)
    thresh2 = cv2.threshold(gray2, 60, 255, cv2.THRESH_BINARY)[1]
        
    fgmask = thresh2 - thresh
    
#    fgmask[fgmask > 200] = 0

    # Display the resulting frame
    cv2.imshow('frame',fgmask)
    cv2.imshow('org',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
