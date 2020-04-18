#!/usr/bin/python

import sys
import os
import random
import time

#print ('Number of arguments:', len(sys.argv), 'arguments.')
#print ('Argument List:', str(sys.argv))

SLEEP_PERIOD = 10 #seconds

while True:
    osCmd = "python3 application/playAudioFileDbIntegration.py"
    print("Invoking: ",osCmd)
    os.system(osCmd)
    time.sleep(SLEEP_PERIOD)