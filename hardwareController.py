import RPi.GPIO as GPIO
import datetime, time
import threading
from threading import Thread
from application.utilities import logger

import sys
sys.path.append('application/')
print(sys.path)

import interface as interface

#pwm = None
#pwmCurrentVal = 0
#pwmTargetValue = 0
#resetTimer = True
#step = 1
#deactivationTimer = None
#timeMarker = 0
lRing = None

class LightRing:
    def __init__(self, gpio):
        self.gpio = gpio
        GPIO.setup(gpio, GPIO.OUT)  #GEN1 - Output - PWM - button light
        self.pwm = GPIO.PWM(gpio, 10000)
        self.pwm.start(0)
        #
        self.pwmCurrentVal=0
        self.pwmTargetValue=0
        self.resetTimer = True
        self.step = 1
        self.timeMarker = 0
        self.stop = False
        self.thatHappenedForTheFirstTime = True
        return

    def run(self):
        delay = 0.015
        if(self.pwmCurrentVal == self.pwmTargetValue):
            delay = 1
        elif(abs(self.pwmCurrentVal-self.pwmTargetValue) < self.step):
            self.pwmCurrentVal = self.pwmTargetValue
        elif(self.pwmCurrentVal > self.pwmTargetValue):
            self.pwmCurrentVal = self.pwmCurrentVal - self.step
        elif(self.pwmTargetValue > self.pwmCurrentVal):
            self.pwmCurrentVal = self.pwmCurrentVal + self.step

        #logger("_INFO_", "Setting pwm to ", pwmCurrentVal)

        if(self.pwmCurrentVal == 100 and self.thatHappenedForTheFirstTime):
            self.thatHappenedForTheFirstTime = False
            self.timeMarker = time.time()

        #if(self.pwmCurrentVal == 100 and self.timeMarker == 0):
        #    logger("_INFO_", "\nSetting TIME MARKER to ", time.time())
        #    self.timeMarker = time.time()
        elif(time.time() - self.timeMarker > 30 and self.pwmCurrentVal == 100 and self.pwmTargetValue != 0):
            logger("_INFO_", "DEACTIVATING LIGHT RING")
            self.pwmTargetValue = 0
            self.thatHappenedForTheFirstTime = True

        if(self.stop == True):
            self.stop = False
            return

        self.pwm.ChangeDutyCycle(self.pwmCurrentVal)
        timer = threading.Timer(delay, self.run)
        timer.daemon = True
        timer.start()
        return
    
    def terminate(self):
        self.pwm.ChangeDutyCycle(0)
        self.stop=True
        return

    def activate(self):
        self.pwmTargetValue = 100
        logger("_INFO_", "Moving time marker from", self.timeMarker, "to", time.time())
        self.timeMarker = time.time()


def motionHandler(channel):
    global lRing
    ts = datetime.datetime.now()
    logger("_INFO_", "\nEvent captured on channel:", channel, ". Current value:", GPIO.input(channel), ". TS:", ts)
    #interface.processTrigger(interface.TriggerType.MOTION)
    t = Thread(target=interface.processTrigger, args=[(interface.TriggerType.MOTION)])
    t.name = "thread_motion_"+str(ts)
    t.start()
    logger("_INFO_", "Thread: ", t.name, "started")
    if(interface.isLightRingActivated()):
        lRing.activate()
    return


def buttonPressHandler(channel):
    global lRing
    ts = datetime.datetime.now()
    logger("_INFO_", "\nEvent captured on channel:", channel, ". Current value:", GPIO.input(channel), ". TS:", ts)
    #interface.processTrigger(interface.TriggerType.MOTION)
    
    #Make interface call only on rising-edge
    if(GPIO.input(channel) == 0):
        return

    t = Thread(target=interface.processTrigger, args=[(interface.TriggerType.BUTTON_PRESS)])
    t.name = "thread_motion_"+str(ts)
    t.start()
    logger("_INFO_", "Thread: ", t.name, "started")
    lRing.activate()
    return

##############   MAIN   ##############
def main():
    global lRing

    logger("_INFO_", "GPIO version: ", GPIO.VERSION)

    #Set pin numbering reference mode
    GPIO.setmode(GPIO.BCM)

    #Setup GPIO as input
    GPIO.setup(17, GPIO.IN)  #GEN2 - Input - motion sensor
    GPIO.setup(27, GPIO.IN)  #GEN2 - button press / on demand

    #PWM
    lRing = LightRing(18)
    lRing.run()


    #GPIO.add_event_detect(18, GPIO.RISING, callback=gpio18_callback, bouncetime=1000)
    GPIO.add_event_detect(17, GPIO.RISING, callback=motionHandler, bouncetime=1000)
    GPIO.add_event_detect(27, GPIO.RISING, callback=buttonPressHandler, bouncetime=100)

    try:
        logger("_INFO_", "Setup complete. Waiting for interrupts")
        while True:
            time.sleep(100)
            #continue

    except KeyboardInterrupt:
        logger("_INFO_", "...Terminating")
        pass

    except:
        logger("_INFO_", "Unknown error")
    
    finally:
        #logger("_INFO_", "Cleaninug up GPIO")
        #GPIO.cleanup()
        lRing.terminate()
        logger("_INFO_", "Not using GPIO.cleanup() with intent to prevent resetting of GPIOs")

    return

if __name__ == "__main__":
    main()