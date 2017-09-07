'''
@author: qian
'''
import time
import numpy as np

class Timer():
    '''
    Control: 
        Timer.start(), Timer.stop(), then the time span is added into a list.
        Timer.reset() to clear the list.
    Result: 
        Timer.cal() to update the numbers, then get Timer.ave or Timer.std
    '''
    __startTime = 0
    __times = []
    ave = 0
    std = 0

    def __init__(self):
        '''
        Constructor
        '''
        self.reset()
    
    def start(self):
        '''
        Start a timer
        '''
        self.__startTime = time.time()

    def stop(self):
        '''
        Stop a timer, and add the time span into the list
        '''
        self.__times.append(time.time()-self.__startTime)
        
    def reset(self):
        '''
        Clear all records
        '''
        self.__times = []
        
    def cal(self,f=None):
        '''
        This function calculate the average of all time pieces and the standard deviation.
        It has to be called before get the average or std value.
        '''
        self.ave = np.mean(self.__times)
        self.std = np.std(self.__times)
        if not f is None:
            f.write(str(self.ave)+','+str(self.std)+',')
        else:
            print "ave "+str(self.ave)
            print "std "+str(self.std)
    
if __name__ == '__main__':
    # example
    testTimer = Timer()
    for i in range(10):
        testTimer.start()
        time.sleep(0.1*i)
        testTimer.stop()
    testTimer.cal()
    print testTimer.ave
    print testTimer.std
        