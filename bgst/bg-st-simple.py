import imutils
import cv2
import numpy as np
# construct the argument parse and parse the arguments
def setCam(cap0,gain,w,h,fps):
    cap0.set(cv2.CAP_PROP_FRAME_WIDTH, w);
    cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, h);
    cap0.set(cv2.CAP_PROP_FPS, fps)
    cap0.set(cv2.CAP_PROP_GAIN,gain)


vs0 = cv2.VideoCapture(1)
setCam(vs0,0.5,320,240,200)
vs1 = cv2.VideoCapture(2)
setCam(vs1,0.55,320,240,200)

def bg_std():
    global mean_frame0, mean_frame1, std_frame0, std_frame1, dims, bg0, bg1
    bg0_list = []
    bg1_list = []
    count = 0
#     flag0, bg0 = vs0.read()
#     flag1, bg1 = vs1.read()
#     bg0 = cv2.cvtColor(bg0,cv2.COLOR_BGR2GRAY)
#     bg1 = cv2.cvtColor(bg1,cv2.COLOR_BGR2GRAY)
    while count<10:
        count+=1
        flag0, frame0 = vs0.read()
        flag1, frame1 = vs1.read()
        frame0 = cv2.cvtColor(frame0,cv2.COLOR_BGR2GRAY)
        frame1 = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
        bg0_list.append(frame0)
        bg1_list.append(frame1)

    dims = bg0_list[0].shape
    bg0_ar = np.array(bg0_list)
    mean_frame0 = np.zeros(dims)
    std_frame0 = np.zeros(dims)

    bg1_ar = np.array(bg1_list)
    mean_frame1 = np.zeros(dims)
    std_frame1 = np.zeros(dims)
    for i in range(dims[0]):
        for j in range(dims[1]):
            mean_frame0[i][j]   = np.mean(bg0_ar[:,i,j])
#             std_frame0[i][j]    = 64*np.std(bg0_ar[:,i,j])
            mean_frame1[i][j]   = np.mean(bg1_ar[:,i,j])
#             std_frame1[i][j]    = 8*np.std(bg1_ar[:,i,j])
    bg0 = cv2.blur(mean_frame0,(5,5))
    bg1 = cv2.blur(mean_frame1,(5,5))

bg_std()
while True:
    flag0, frame0 = vs0.read()
    flag1, frame1 = vs1.read()
    if not flag0:# or not flag1:
        break
    gray0 = cv2.cvtColor(frame0,cv2.COLOR_BGR2GRAY)
    gray1 = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
    thresh0 = cv2.threshold(gray0, 40, 255, cv2.THRESH_BINARY)[1]
    thresh1 = cv2.threshold(gray1, 40, 255, cv2.THRESH_BINARY)[1]
    bgray0 = cv2.blur(gray0,(5,5))
    bgray1 = cv2.blur(gray1,(5,5))
    dist0 = abs(bgray0-bg0)#  - std_frame0
    dist1 = abs(bgray1-bg1)#  - std_frame0
    sub0 = thresh0 - dist0
    sub0[sub0<0]=0
#     sub0[sub0>235]=0
    sub1 = thresh1 - dist1
    sub1[sub1<0]=0
    sub1[sub1>235]=0
    sub0 = cv2.threshold(sub0, 235, 255, cv2.THRESH_TOZERO_INV)[1]
    sub0 = cv2.threshold(sub0, 0, 255, cv2.THRESH_BINARY)[1]
    sub1 = cv2.threshold(sub1, 0, 255, cv2.THRESH_BINARY)[1]
    cv2.imshow("BS0", sub0.astype(np.uint8))
    cv2.imshow("BS1", sub1.astype(np.uint8))

    
#     cv2.imshow("ORG0", gray0.astype(np.uint8))
#     cv2.imshow("ORG1", frame1)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

# do a bit of cleanup
cv2.destroyAllWindows()
