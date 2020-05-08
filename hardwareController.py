import RPi.GPIO as GPIO
import datetime, time
import threading
from threading import Thread
from application.utilities import logger

import sys
sys.path.append('application/')
print(sys.path)

import interface as interface

pwm = None
pwmCurrentVal = 0
pwmTargetValue = 0
resetTimer = True
step = 1
deactivationTimer = None
timeMarker = 0

def lightRingInertialEngine():
    global pwm, pwmTargetValue, step, pwmCurrentVal, deactivationTimer, timeMarker

    # If it is already at 100, set a timer thread to rev it down 
    #if(pwmCurrentVal == 100):
    #    # this thread will set the targetValue to 0 in 30 seconds
    #    return
    #else:
    #    pwmTargetValue = 100
    delay = 0.01
    #if(resetTimer):
    #    resetTimer = False
    #    if(deactivationTimer != None):
    #        logger("_INFO_", "\nCANCELLING EXISTING TIMER")
    #        deactivationTimer.cancel()
    #        deactivationTimer = None

    if(pwmCurrentVal == pwmTargetValue):
        #timer = threading.Timer(0.1, lightRingInertialEngine)
        #timer.start()
        #return
        delay = 1
    elif(abs(pwmCurrentVal-pwmTargetValue) < step):
        pwmCurrentVal = pwmTargetValue
    elif(pwmCurrentVal > pwmTargetValue):
        pwmCurrentVal = pwmCurrentVal - step
    elif(pwmTargetValue > pwmCurrentVal):
        pwmCurrentVal = pwmCurrentVal + step

    #logger("_INFO_", "Setting pwm to ", pwmCurrentVal)

    if(pwmCurrentVal == 100 and timeMarker == 0):
        logger("_INFO_", "\nSETTING TIME MARKER AT ", time.time())
        timeMarker = time.time()
    elif(time.time() - timeMarker > 30 and pwmCurrentVal == 100 and pwmTargetValue != 0):
        logger("_INFO_", "\nDEACTIVATING LIGHT RING")
        pwmTargetValue = 0

    pwm.ChangeDutyCycle(pwmCurrentVal)
    timer = threading.Timer(delay, lightRingInertialEngine)
    timer.start()

    #if(pwmCurrentVal == 100 and deactivationTimer == None):
    #    logger("_INFO_", "Starting deactivation timer")
    #    deactivationTimer = threading.Timer(30, deactivateLightRing)
    #    deactivationTimer.start()
    return

#def deactivateLightRing():
#    global pwmTargetValue
#    logger("_INFO_", "\nDEACTIVATING LIGHT RING")
#    pwmTargetValue = 0
#    return

#This is called from motionHandler whenever motion is detected.
def activateLightRing():
    global pwmTargetValue, timeMarker
    # It sets pwmTargetValue to 100
    pwmTargetValue = 100
    timeMarker = 0
    return

def motionHandler(channel):
    global pwm, pwmCurrentVal, pwmTargetValue
    ts = datetime.datetime.now()
    logger("_INFO_", "\nEvent captured on channel:", channel, ". Current value:", GPIO.input(channel), ". TS:", ts)
    #interface.processTrigger(interface.TriggerType.MOTION)
    t = Thread(target=interface.processTrigger, args=[(interface.TriggerType.MOTION)])
    t.name = "thread_motion_"+str(ts)
    t.start()
    logger("_INFO_", "Thread: ", t.name, "started")
    activateLightRing()
    return


def buttonPressHandler(channel):
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
    return

##############   MAIN   ##############
def main():
    global pwm

    logger("_INFO_", "GPIO version: ", GPIO.VERSION)

    #Set pin numbering reference mode
    GPIO.setmode(GPIO.BCM)

    #Setup GPIO as input
    GPIO.setup(17, GPIO.IN)  #GEN2 - Input - motion sensor
    GPIO.setup(27, GPIO.IN)  #GEN2 - button press / on demand

    #PWM
    GPIO.setup(18, GPIO.OUT)  #GEN1 - Output - PWM - button light
    pwm = GPIO.PWM(18, 10000)
    pwm.start(0)
    lightRingInertialEngine()


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
        logger("_INFO_", "Not using GPIO.cleanup() with intent to prevent resetting of GPIOs")

    return

if __name__ == "__main__":
    main()