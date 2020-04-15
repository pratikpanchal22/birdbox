import RPi.GPIO as GPIO
import time

print("GPIO version: ", GPIO.VERSION)

#Set pin numbering reference mode
GPIO.setmode(GPIO.BCM)

#Setup GPIO as input
GPIO.setup(17, GPIO.IN)  #GEN2 - button press / on demand
GPIO.setup(18, GPIO.IN)  #GEN1 - motion sensor
GPIO.setup(27, GPIO.IN)  #GEN2 - Disable 

def gpio18_callback(channel):
    input_value = GPIO.input(18)
    print("GPIO18: ", input_value)

def gpio17_callback(channel):
    input_value = GPIO.input(17)
    print("GPIO17: ", input_value)


GPIO.add_event_detect(18, GPIO.FALLING, callback=gpio18_callback, bouncetime=1000)

try:
    #print ("Waiting for rising edge on port 24")
    #GPIO.wait_for_edge(24, GPIO.RISING)
    #print ("Rising edge detected on port 24")
    while True:
        time.sleep(100)
        #continue

except KeyboardInterrupt:
    print("...Terminating")
    pass
    #GPIO.cleanup()
#GPIO.cleanup()