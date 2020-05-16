import threading  
import time 
import subprocess 
from dateutil import parser
from datetime import timedelta, datetime
from interface import logger

import subprocess
import re
import threading  

class AlsaVolume:
    targetVolume = 75
    #currentVolume = 0
    step = 1
    interval = 0.0001

    #def __init__(self):
    #    return

    @classmethod
    def getCurrentVolume(cls, *argv):
        cmd = ['amixer']

        try:
            vs = argv[0]
            cmd.extend(['set', 'PCM', vs])
        except:
            cmd.extend(['get', 'PCM'])
        
        print(cmd)
        
        #parse current volume here and return from here
        r = subprocess.check_output(cmd)
        string = r.decode("utf-8")
        #print("output: ", string)
        sg = re.search(' \[(.*)\%\] ', string)
        volume = sg.group(1)
        #print("Extracted volume: ", volume)
        return int(volume)
    
    @classmethod
    def setVolume(cls, vol):
        if(vol < 0):
            vol = 0
        elif(vol > 100):
            vol = 100

        AlsaVolume.targetVolume = vol
        cv = cls.getCurrentVolume() 
        if(cv != cls.targetVolume):
            cls.__driftToTarget(cv)
        return

    @classmethod
    def __driftToTarget(cls, cv):
        
        #print("Drifting: cv=", cv, "  target=", cls.targetVolume)
        if(cls.targetVolume == cv):
            return
        elif(cls.targetVolume > cv):
            cv += cls.step
        else:
            cv -= cls.step

        cv = cls.getCurrentVolume(str(cv)+'%')

        t = threading.Timer(cls.interval, cls.__driftToTarget, args = [cv])
        t.start()
        return

#if __name__ == '__main__':
#    print("\nEntering Alsa volume main")
#    print(AlsaVolume.getCurrentVolume())
#    AlsaVolume.setVolume(100)
    

class AudioThread(threading.Thread):
    instanceCount = 0
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)

        logger("_INFO_", "\n>>>> Initializing a new AudioThread Object")

        #private
        self._pCurrent = None
        self._pNext = None
        self._rerun = True
        self._repeat = True
        self._pbStartTime = 0
        self._pbStartTimeStatic = 0
        self._futureTerminationCallback = None
        self.terminateAt = None
        
        try:
            self.fp = kwargs['fp']
        except KeyError:
            logger("_INFO_", 'Error: fp (file path) is a required argument')
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
            self.setFutureTerminationTime(kwargs['terminateAt'])
        except KeyError:
            self.terminateAt = None

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
            
        logger("_INFO_", "File: ", self.fp)
        logger("_INFO_", "Thread name: ", self.name)
        logger("_INFO_", "Volume: ", self.vol)    
        logger("_INFO_", "Frames per millisecond: ", self.framePerMs)
        logger("_INFO_", "Starting frame: ", self.startingFrame)
        logger("_INFO_", "Switching offset: ", self.switchingOffset)

        AudioThread.instanceCount += 1
        logger("_INFO_", "AudioThread instance count: ", AudioThread.instanceCount)
        return    

    def run(self):
        logger("_INFO_", "\na.run")
        self._pbStartTimeStatic = time.monotonic()

        self.__startSelf()
        while self._rerun == True:
            self._pCurrent.wait()
            if(self._pNext == None):
                if(self._repeat == True):
                    self.__startSelf()
                else:
                    self._rerun = False
            else:
                self._pCurrent = self._pNext
                self._pNext = None

        #self.terminate()
        logger("_INFO_", "------END OF RUN-------")
        return

    def getName(self):
        return self.name

    def runTime(self):
        return time.monotonic() - self._pbStartTimeStatic

    def changeVolume(self, volume):
        if(self.vol != volume):
            logger("_INFO_", "Changing vol to:", volume)    
            self.vol = volume
            self.__atSameFrameSwitchTrack()
        return

    def setFutureTerminationTime(self, terminationTime):
        if(self.terminateAt == terminationTime):
            return
        
        try:
            futureTime = parser.parse(terminationTime)
        except:
            logger("_INFO_", "Error: Unknown terminationTime: ", str(terminationTime))
            return

        self.terminateAt = terminationTime
        logger("_INFO_", "Changing termination time to:", self.terminateAt)    

        if(self._futureTerminationCallback != None):
            self._futureTerminationCallback.cancel()
            self._futureTerminationCallback = None
        
        #compute time
        currentTime = datetime.now()
        if(currentTime>futureTime):
            futureTime += timedelta(hours=24)

        secondsToTerminate = (futureTime-currentTime).total_seconds()
        logger("_INFO_", "Setting up termination for ", terminationTime, " in ", secondsToTerminate, " seconds")
        self._futureTerminationCallback = threading.Timer(secondsToTerminate, self.terminate, args=[])
        self._futureTerminationCallback.start()
        return

    def terminate(self):
        logger("_INFO_", "\na.terminate")
        self._rerun = False
        self._repeat = False
        if(self._pCurrent != None):
            self._pCurrent.kill()
            self._pCurrent = None
        if(self._pNext != None):
            self._pNext.kill()
            self._pNext = None
        if(self._futureTerminationCallback != None):
            self._futureTerminationCallback.cancel()
        return

    def changeFile(self, fp):
        if(fp != self.fp):
            logger("_INFO_", "Changing file to:", fp)
            self.fp = fp
            self._pbStartTime = round(time.monotonic() * 1000)
            self.__atSameFrameSwitchTrack()
        return

    def __startSelf(self):
        self._pbStartTime = round(time.monotonic() * 1000)
        logger("_INFO_", "Start time: ", self._pbStartTime, datetime.now())
        logger("_INFO_", "Command: ", self.__command())
        self._pCurrent = subprocess.Popen("exec " + self.__command(), stdout=subprocess.PIPE, shell=True)
        return

    def __command(self):
        return "mpg321 --gain "+str(self.vol)+" -q -k " +str(self.startingFrame)+ " " + self.fp

    def __atSameFrameSwitchTrack(self):
        logger("_INFO_", "Running with cmd: ", self.__command())            
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
    logger("_INFO_", "State of thread: a.isAlive: ", a.isAlive())
    time.sleep(15)
    logger("_INFO_", "State of thread: a.isAlive: ", a.isAlive())
    a.changeVolume(30)
    time.sleep(4)
    a.changeVolume(10)
    time.sleep(4)
    a.terminate()


        

