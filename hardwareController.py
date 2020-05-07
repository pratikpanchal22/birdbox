import RPi.GPIO as GPIO
import datetime, time
from threading import Thread
from application.utilities import logger

import sys
sys.path.append('application/')
print(sys.path)

import interface as interface

pwm = ""
pwmVal = 0

def motionHandler(channel):
    global pwm, pwmVal
    ts = datetime.datetime.now()
    logger("_INFO_", "\nEvent captured on channel:", channel, ". Current value:", GPIO.input(channel), ". TS:", ts)
    #interface.processTrigger(interface.TriggerType.MOTION)
    t = Thread(target=interface.processTrigger, args=[(interface.TriggerType.MOTION)])
    t.name = "thread_motion_"+str(ts)
    t.start()
    logger("_INFO_", "Thread: ", t.name, "started")
    if(pwmVal == 0):
        pwmVal = 100
    else:
        pwmVal = 0
    
    pwm.ChangeDutyCycle(pwmVal)
    return


def buttonPressHandler(channel):
    ts = datetime.datetime.now()
    logger("_INFO_", "\nEvent captured on channel:", channel, ". Current value:", GPIO.input(channel), ". TS:", ts)
    #interface.processTrigger(interface.TriggerType.MOTION)
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
    pwm = GPIO.PWM(18, 5000)
    pwm.start(0)


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