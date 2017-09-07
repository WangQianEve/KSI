'''
Created on Aug 15, 2017

@author: qian
'''
import cv2
import numpy as np
class BackgroundSubtractor():
    '''
    BackgroundSubtractor do background subtraction with multiple choices. 
    Construct with a parameter indicating which method to use and parameters.
    Call bgst(frame) function to do background subtraction
    '''
    def __init__(self,type,roi=0,scfSize=0,scfThresh=0,gause=0,sbsThresh=-1,sbsThreshL=40,sbsThreshH=235):
        '''
        Constructor for skinColor algorithm.
        roi: path of sample image
        scfSize: Structural element size
        scfThresh: brightness threshold
        '''
        self.__type = type
        if type=="sbs":
            self.__sbsThreshL = sbsThreshL
            self.__sbsThreshH = sbsThreshH
            self.__gause = gause
        elif type=="bright":
            self.__bThresh = sbsThresh
            self.__gause = gause
        else:
            self.__roihist = self.__getRoihist(roi)
            self.__scfSize = tuple(scfSize)
            self.__scfThresh = scfThresh
            self.__gause = gause
    
    def setBThresh(self,th,gause):
        self.__bThresh = th
        self.__gause = gause
    
    def setThresh(self,l,h):
        self.__sbsThreshL = l
        self.__sbsThreshH = h
        
    def blurBg(self,gause):
        self.__gause = gause
        self.__sbsBg = cv2.blur(self.mean,(self.__gause,self.__gause)) ##
        
    def setBgM(self,cap,cc):
        print "sampling"
        bg0_list = []
        count = 0
        while count<cc:
            count+=1
            flag0, frame0 = cap.read()
            frame0 = cv2.cvtColor(frame0,cv2.COLOR_BGR2GRAY)
            bg0_list.append(frame0)
    
        dims = bg0_list[0].shape
        bg0_ar = np.array(bg0_list)
        mean_frame0 = np.zeros(dims)
        for i in range(dims[0]):
            for j in range(dims[1]):
                mean_frame0[i][j]   = np.mean(bg0_ar[:,i,j])
        self.mean = mean_frame0
        self.__sbsBg = cv2.blur(mean_frame0,(self.__gause,self.__gause)) ##

    def setBg(self,cap):
        print "sampling"
        ret, still = cap.read()
        gray_still = cv2.cvtColor(still, cv2.COLOR_BGR2GRAY)
#         blur = cv2.bilateralFilter(gray_still, 9, 75, 75)
        gray_still = cv2.blur(gray_still,(self.__gause,self.__gause))
        thresh = cv2.threshold(gray_still, self.__sbsThresh, 255, cv2.THRESH_BINARY)[1]
        self.__sbsBg = thresh
                
    def __getRoihist(self,roi):
        '''
        This function use a sample image roi to produce the histgram of it.
        It returns the histgram, which will be used in skin color filter algorithm.
        roi: the path of sample image.
        output: histgram of this sample
        '''
        roi = cv2.imread(roi)
        hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
        roihist = cv2.calcHist([hsv],[0, 1], None, [180, 256], [0, 180, 0, 256] )
        cv2.normalize(roihist,roihist,0,255,cv2.NORM_MINMAX)
        return roihist
    
    def __skinColor(self,frame):
        '''
        This function use skin color filter to do background subtraction. Only called by bgst()
        It returns a binary color image.
        frame: RGB image that need background subtraction
        output: Grayscale image that contains only black and white pixels
        '''
        if self.__gause>0:
            frame = cv2.GaussianBlur(frame,(self.__gause,self.__gause),0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0,1], self.__roihist, [0,180,0,256], 1)
        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, self.__scfSize)
        cv2.filter2D(dst, -1, disc, dst)
        ret, thresh = cv2.threshold(dst, self.__scfThresh, 255, 0)
        return thresh
        
    def __brightness(self,frame):
        gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         blur2 = cv2.bilateralFilter(gray2, 9, 75, 75)
#         gray2 = cv2.GaussianBlur(gray2,(5,5),0)
        gray2 = cv2.blur(gray2,(self.__gause,self.__gause))
        thresh2 = cv2.threshold(gray2, self.__sbsThresh, 255, cv2.THRESH_BINARY)[1]
        sbsBg = cv2.threshold(self.__sbsBg, self.__sbsThresh, 255, cv2.THRESH_BINARY)[1]
        fgmask = thresh2 - sbsBg
        return fgmask
    
    def __simple(self,frame0,preprocess=False):
        gray0 = cv2.cvtColor(frame0,cv2.COLOR_BGR2GRAY)
        gray0 = cv2.blur(gray0,(self.__gause,self.__gause)) ##
        thresh0 = cv2.threshold(gray0, self.__sbsThreshL, 255, cv2.THRESH_BINARY)[1]
        if preprocess:
            return thresh0
        dist0 = abs(gray0-self.__sbsBg)
        sub0 = thresh0 - dist0
#         gray0 = cv2.blur(gray0,(self.__gause,self.__gause)) ##
        sub0[sub0<0]=0
#         sub0[sub0>self.__sbsThreshH]=0
        sub0 = cv2.threshold(sub0, self.__sbsThreshH, 255, cv2.THRESH_TOZERO_INV)[1]
        return sub0.astype(np.uint8)

    def bgst(self,frame, orgThresh=False):
        '''
        This function calls other inner functions based on which type this subtractor is to do background subtraction on frame
        It returns a binary color image.
        frame: RGB image that need background subtraction
        output: Grayscale image that contains only black and white pixels
        '''
        if self.__type=="scf":
            return self.__skinColor(frame)
        elif self.__type=="bright":
            return self.__brightness(frame)
        elif self.__type=="sbs":
            return self.__simple(frame,orgThresh)
