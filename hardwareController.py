import RPi.GPIO as GPIO
import datetime, time
from threading import Thread
from application.utilities import logger

import sys
sys.path.append('application/')
print(sys.path)

import interface as interface

def gpio18_callback(channel):
    ts = datetime.datetime.now()
    input_value = GPIO.input(18)
    logger("_INFO_", "\nGPIO18: ", input_value,"Motion detected at ",ts)
    #interface.processTrigger(interface.TriggerType.MOTION)
    t = Thread(target=interface.processTrigger, args=[(interface.TriggerType.MOTION)])
    t.name = "thread_motion_"+str(ts)
    t.start()
    logger("_INFO_", "Thread: ", t.name, "started")

def gpio17_callback(channel):
    input_value = GPIO.input(17)
    logger("_INFO_", "GPIO17: ", input_value)

##############   MAIN   ##############
def main():
    logger("_INFO_", "GPIO version: ", GPIO.VERSION)

    #Set pin numbering reference mode
    GPIO.setmode(GPIO.BCM)

    #Setup GPIO as input
    GPIO.setup(17, GPIO.IN)  #GEN2 - button press / on demand
    GPIO.setup(18, GPIO.IN)  #GEN1 - motion sensor
    GPIO.setup(27, GPIO.IN)  #GEN2 - Disable 

    GPIO.add_event_detect(18, GPIO.RISING, callback=gpio18_callback, bouncetime=1000)

    try:
        logger("_INFO_", "Setup complete. Waiting for interrupts")
        while True:
            time.sleep(100)
            #continue

    except KeyboardInterrupt:
        logger("_INFO_", "...Terminating")
        pass
        #GPIO.cleanup()
    #GPIO.cleanup()
    return

if __name__ == "__main__":
    main()