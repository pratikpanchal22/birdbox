import threading  
import time 
import subprocess 
from dateutil import parser
from datetime import timedelta, datetime

class AudioThread(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)

        #private
        self._pCurrent = None
        self._pNext = None
        self._rerun = True
        self._pbStartTime = 0
        self._pbStartTimeStatic = 0
        self._futureTerminationCallback = None
        
        try:
            self.fp = kwargs['fp']
        except KeyError:
            print('Error: fp (file path) is a required argument')
            exit()

        try:
            self.name = kwargs['tName']
        except KeyError:
            self.name = "AudioThread"+str(round(time.monotonic() * 1000))

        try:
            self.vol = kwargs['volume']
        except KeyError:
            self.vol = 100

        try:
            self.framePerMs = kwargs['fpms']            
        except KeyError:
            self.framePerMs = 0.0382848

        try:
            self.startingFrame = kwargs['startingFrame']
        except KeyError:
            self.startingFrame = 0

        try:
            self.switchingOffset = kwargs['swOffset']
        except KeyError:
            self.switchingOffset = 0.6

        try:
            self.terminateAt = kwargs['terminateAt']
            self.setFutureTerminationTime(self.terminateAt)
        except KeyError:
            self.terminateAt = 0
            
        print("File: ", self.fp)
        print("Thread name: ", self.name)
        print("Volume: ", self.vol)    
        print("Frames per millisecond: ", self.framePerMs)
        print("Starting frame: ", self.startingFrame)
        print("Switching offset: ", self.switchingOffset)

        return    

    def run(self):
        print("\na.run")
        self._pbStartTimeStatic = time.monotonic()

        self._pbStartTime = round(time.monotonic() * 1000)
        print("Start time: ", self._pbStartTime)
        self._pCurrent = subprocess.Popen("exec " + self.__command(), stdout=subprocess.PIPE, shell=True)
        while self._rerun == True:
            self._pCurrent.wait()
            if(self._pNext == None):
                self._rerun = False
            else:
                self._pCurrent = self._pNext
                self._pNext = None

        print("------END OF RUN-------")
        return

    def setFutureTerminationTime(self, terminationTime):
        if(self._futureTerminationCallback != None):
            self._futureTerminationCallback.cancel()
            self._futureTerminationCallback = None
        else:
            #compute time
            currentTime = datetime.now()
            futureTime = parser.parse(terminationTime)
            if(currentTime>futureTime):
                futureTime += timedelta(hours=24)

            secondsToTerminate = (futureTime-currentTime).total_seconds()
            print("Setting up termination for ", terminationTime, " in ", secondsToTerminate, " seconds")
            self._futureTerminationCallback = threading.Timer(secondsToTerminate, self.terminate, args=[])
            self._futureTerminationCallback.start()
        return

    def runTime(self):
        return time.monotonic() - self._pbStartTimeStatic

    def changeVolume(self, volume):
        print("\na.changeVolume")
        if(self.vol != volume):    
            self.vol = volume
            self.__switchTrack()
        return

    def changeFile(self, fp):
        self.fp = fp
        self._pbStartTime = round(time.monotonic() * 1000)
        self.__switchTrack()
        return

    def terminate(self):
        print("\na.terminate")
        self._rerun = False
        if(self._pCurrent != None):
            self._pCurrent.kill()
            self._pCurrent = None
        if(self._pNext != None):
            self._pNext.kill()
            self._pNext = None
        return

    def __command(self):
        return "mpg321 --gain "+str(self.vol)+" -q -k " +str(self.startingFrame)+ " " + self.fp

    def __switchTrack(self):
        print("a.run: Running with cmd: ", self.__command())            
        #Compute new frame
        self.startingFrame = round((round(time.monotonic() * 1000) - self._pbStartTime) * self.framePerMs)        
        self._pNext = subprocess.Popen("exec " + self.__command(), stdout=subprocess.PIPE, shell=True)
        #Set timer to kill old process
        timer = threading.Timer(self.switchingOffset, self.__killProcess, args=[self._pCurrent])
        timer.start()
        return

    def __killProcess(self, p):
        p.kill()
        return

    
if __name__ == '__main__':
    a = AudioThread(fp="GregoryAlanIsakov3am.mp3", swOffset=0.75)
    a.start()
    time.sleep(10)
    a.changeVolume(70)
    print("State of thread: a.isAlive: ", a.isAlive())
    time.sleep(15)
    print("State of thread: a.isAlive: ", a.isAlive())
    a.changeVolume(30)
    time.sleep(4)
    a.changeVolume(10)
    time.sleep(4)
    a.terminate()


        

