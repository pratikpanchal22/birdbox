import threading
import time 
from datetime import timedelta, datetime
from dateutil import parser  
#
from common.utility import logger

class CustomizableTimerThread(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.terminateAt = None
        self._futureTerminationCallback = None

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
        return