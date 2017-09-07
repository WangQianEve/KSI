'''
This script is to see the code of different key
@author: qian
'''
import cv2

if __name__ == '__main__':
    vs0 = cv2.VideoCapture(0)
    while True:
        (grabbed0, frame0) = vs0.read()
        cv2.imshow("Frame0", frame0)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break  
        if key!=255:
            print key

    vs0.release()
    cv2.destroyAllWindows()
