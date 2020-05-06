import os
import random
import models as models
from enum import Enum
from threading import Thread, current_thread
import inspect
from utilities import logger
import json
import dbConfig as dbc
from dateutil import parser
import datetime

#TRIGGER TYPES
class TriggerType(Enum):
    UNSUPPORTED_TRIGGER = 0
    MOTION = 1
    ON_DEMAND_SOLO = 2
    ON_DEMAND_SYMPHONY = 3
    ALARM = 3 

#CANDIDATE SELECTION MODELS
class CandidateSelectionModels(Enum):
    RNDM_TOP_75PC = 1   #Random candidate from top 75% of set that was sorted by last updated time with oldest on top

#GLOBALS - TODO: Move to persistent storage
randomizeNumberOfChannels = True #TODO: get this from settings
appSettings = ""

def updateGlobalSettings():
    global appSettings
    try:
        appSettings = json.loads(models.fetchModel(models.ModelType.APP_SETTINGS)[0][dbc.KEY_SETTINGS])
    except:
        logger("_ERROR_", "appSettings[0][dbc.KEY_SETTINGS] doesn't exist")
    return

def isSilentPeriodActive():
    dv = False
    try:
        silentPeriodEnabled = appSettings[dbc.KEY_SILENT_PERIOD][dbc.KEY_ENABLED]
        silenStartTime = parser.parse(appSettings[dbc.KEY_SILENT_PERIOD][dbc.KEY_START_TIME])
        silentEndTime = parser.parse(appSettings[dbc.KEY_SILENT_PERIOD][dbc.KEY_END_TIME])
    except:
        logger("_ERROR_", "appSettings doesn't exist")
        return dv

    if(silentPeriodEnabled == False):
        return False

    #Local time
    currentTime = datetime.datetime.now()
    logger("_INFO_","    ** silentStartTime = ", silenStartTime)
    logger("_INFO_","    ** currentTime = ", currentTime)
    logger("_INFO_","    ** silentEndTime = ", silentEndTime)
    if(silenStartTime <= currentTime < silentEndTime):
        return True

    return dv
    
def isMotionTriggerActive():
    #Default
    dv = True
    try:
        dv = appSettings[dbc.KEY_MOTION_TRIGGERS][dbc.KEY_ENABLED] 
    except:
        logger("_ERROR_", "appSettings[dbc.KEY_MOTION_TRIGGERS][dbc.KEY_ENABLED] doesn't exist")
    return dv

def maxNumberOfAllowedSimultaneousChannels():
    #Default
    dv = 5
    try:
        dv = int(appSettings[dbc.KEY_SYMPHONY][dbc.KEY_MAXIMUM])
    except:
        logger("_ERROR_", "appSettings[dbc.KEY_SYMPHONY][dbc.KEY_MAXIMUM] doesn't exist")
    return dv

def isBirdChoiceLimitedToSameSpecies():
    #Default
    dv = False
    try:
        dv = appSettings[dbc.KEY_SYMPHONY][dbc.KEY_LIMIT_TO_SAME_SPECIES] 
    except:
        logger("_ERROR_", "appSettings[dbc.KEY_SYMPHONY][dbc.KEY_LIMIT_TO_SAME_SPECIES] doesn't exist")
    return dv

def maxVolume():
    #Default
    dv = 100
    try:
        dv = int(appSettings[dbc.KEY_VOLUME])
    except:
        logger("_ERROR_", "appSettings[dbc.KEY_VOLUME] doesn't exist")
    return dv

def isContinuousPlaybackEnabled():
    return False

###################################################
##########  ~~~ TRIGGER TYPE: MOTION ~~~ ##########
###################################################
def processMotionTrigger(**kwargs):
    #print("\n--> ",inspect.stack()[0][3], " CALLED BY ",inspect.stack()[1][3])

    #TODO: Right now don't see any need to push motion events in db. So skipping. 
    #But if required, this will be the place to do so. 

    #Validations
    #1. Verify that not in silent period
    if(isSilentPeriodActive()):
        logger("_INFO_", "Silent period active. Exiting")
        return

    #2. TODO: Verify that required time has passed since last playback
    
    #Purge dead entries
    #Fetch
    activeEntries = models.fetchModel(models.ModelType.ACTIVE_ENTRIES)
    activeEntries = [d[dbc.KEY_ID] for d in activeEntries]

    #3. Verify that number of active entries don't exceed maximum allowed
    if(len(activeEntries) > 0):
        purged = purgeDeadEntries(60)
        if(purged > 0):
            logger("_INFO_", purged, "Entries purged")
            activeEntries = models.fetchModel(models.ModelType.ACTIVE_ENTRIES)

    logger("_INFO_", "Active entries:", activeEntries)
    logger("_INFO_", "Active/maxAllowed=", len(activeEntries), "/", maxNumberOfAllowedSimultaneousChannels())
    if(len(activeEntries) >= maxNumberOfAllowedSimultaneousChannels()):
        logger ("_INFO_", "Ignoring trigger. Exiting\n")
        return

    #4. Compute number of channels to implement if not provided
    if (kwargs.get("triggerType") == "solo"):
        numberOfChannels = 1
    elif (kwargs.get("triggerType") == "symphony"):         
        numberOfChannels = maxNumberOfAllowedSimultaneousChannels() - len(activeEntries)
    elif (kwargs.get("triggerType") == "motion"):
        if(randomizeNumberOfChannels):
            numberOfChannels = random.randint(1, maxNumberOfAllowedSimultaneousChannels()-len(activeEntries))
        else:
            numberOfChannels = maxNumberOfAllowedSimultaneousChannels() - len(activeEntries)
    
    candidates = getCandidateAudioFiles(CandidateSelectionModels.RNDM_TOP_75PC, numberOfChannels)
    
    #print("Candidate audio files:")
    logger("_INFO", "\nFINAL CANDIDATES. Requesting:")
    threads = []
    for c in candidates:
        logger("_INFO_", "{:>4.4} {:32.32} {}".format(str(c[dbc.KEY_ID]),c[dbc.KEY_NAME],c[dbc.KEY_AUDIO_FILE]))
        t = Thread(target=executeAudioFileOnSeparateThread, args=[c[dbc.KEY_ID], c[dbc.KEY_AUDIO_FILE]])
        t.name = "thread_id_"+str(c[dbc.KEY_ID])
        threads.append(t)

    #Start threads
    for t in threads:
        t.start()    
        logger("_INFO_", " {} {:<10} {} {:<10}".format("Thread: ", str(t.name), "Status: ", str(t.isAlive())))

    #Wait on threads
    for t in threads:
        t.join()

    logger("_INFO_", "{} {}".format("ALL CHILD THREADS COMPLETED: for parent thread: ", str(current_thread().name)))    
    return

def purgeDeadEntries(seconds):    
    return int(models.fetchModel(models.ModelType.UNSET_ACTIVE_FOR_DEAD_ENTRIES, seconds))

def executeAudioFileOnSeparateThread(id, file):
    #print("\n--> ",inspect.stack()[0][3], " CALLED BY ",inspect.stack()[1][3])
    #Use Id to mark entry as active
    models.fetchModel(models.ModelType.FOR_ID_SET_ACTIVE_UPDATE_TS, id)
    #logger("Id: ",id, " marked as active")

    #Run audio file
    #audioCmd = "mpg321 --gain 10 --verbose --quiet"
    audioCmd = "mpg321 --gain "+str(maxVolume())+" --quiet"
    #logger("_INFO", "os command running from directory: ")
    #os.system("pwd")
    basePath = "/home/pratikpanchal/virtualSandbox/birdbox/application/static/sounds/"
    osCmd = audioCmd + " " + basePath + file
    #logger("_INFO_","os.command: ",osCmd)
    os.system(osCmd)
    
    #Use Id to mark entry as inactive
    models.fetchModel(models.ModelType.FOR_ID_UNSET_ACTIVE, id)
    logger("_INFO_", "End of executeAudioFileOnSeparateThread for ", file, "id=", id)
    return    

def getCandidateAudioFiles(modelType, numberOfChannels):
    #print("\n--> ",inspect.stack()[0][3], " CALLED BY ",inspect.stack()[1][3])
    if(numberOfChannels == 0):
        return
    
    #Scope: 
    # (1) Fetch all sorted by last_updated asc
    data = models.fetchModel(models.ModelType.IDS_NAMES_AUDIOFILE_SORTED_BY_LAST_UPDATED_OLDEST_FIRST)
    # (2) Select one t random from top 75% of that list
    #for d in data:
    #    print("New line")
    #    print(d[0])
    #    print(d[1])

    logger("_INFO_", "Total data rows: ",len(data))
    #print(type(data))
    #for d in data:
    #    print(type(d))
    #print(data)
    #print("\nJSON dumps:",json.dumps(data))
    
    allIds = [d[dbc.KEY_ID] for d in data]
    logger("_INFO_", allIds)
    eligibleLength = int(0.75 * len(data))
    candidates = []
    
    #Choose first at random
    candidates.append(data[random.randint(0, eligibleLength-1)])
    logger("_INFO_", "CHOOSING 1st candidate:")
    logger("_INFO_", "{:>4.4} {:32.32} {}".format(str(candidates[0][dbc.KEY_ID]),candidates[0][dbc.KEY_NAME],candidates[0][dbc.KEY_AUDIO_FILE]))
    data.remove(candidates[0])

    #Remove last 25%
    indicesToRemove = len(data) - eligibleLength
    for i in range(0, indicesToRemove):
        data.remove(data[len(data)-1])

    logger("_INFO_", "Total number of channels to implement: ", numberOfChannels)

    if(numberOfChannels > 1):
        speciesConstrainedSet = []
        logger("INFO_", "Limit to same species: ", isBirdChoiceLimitedToSameSpecies())
        if(isBirdChoiceLimitedToSameSpecies()):
            for d in data:
                if(d == candidates[0]):
                    print(d," :Already exists. Skipping")
                    #data.remove(candidates[0])
                    continue
                elif(d[dbc.KEY_NAME] == candidates[0][dbc.KEY_NAME]):
                    speciesConstrainedSet.append(d)
            data = speciesConstrainedSet

        logger("_INFO_", "Curated candidate data set: size=",len(data))
        for element in data:
            logger("_INFO_", "{:>4.4} {:32.32} {}".format(str(element[dbc.KEY_ID]),element[dbc.KEY_NAME],element[dbc.KEY_AUDIO_FILE]))
    
        if(numberOfChannels >= len(data)):
            logger("_INFO_", "Number of channels to implement "+numberOfChannels+" is more or equal to data set at hand ",len(data))
            for d in data:
                candidates.append(d)
        else:
            for i in range(0, numberOfChannels-1):
                logger("_INFO_", "\nSelecting For channel ",i+2)
                randomlyChosenRowIdx = random.randint(0,len(data)-1)
                logger("_INFO_", "Size of data:",len(data), "  Chosen idx:",randomlyChosenRowIdx, "id={} {} {}".format(str(data[randomlyChosenRowIdx][dbc.KEY_ID]),data[randomlyChosenRowIdx][dbc.KEY_NAME],data[randomlyChosenRowIdx][dbc.KEY_AUDIO_FILE]))
                candidates.append(data[randomlyChosenRowIdx])
                #remove that row to avoid duplication
                data.remove(data[randomlyChosenRowIdx])

    #logger("_INFO_", "Final candidate list: ")
    #candidateAudioFiles = []
    #for c in candidates:
    #    print (c)
    #    candidateAudioFiles.append(c[1])
    
    return candidates

####################################################################################
def processTrigger(triggerType):
    #logger("_INFO_", "\n--> ",inspect.stack()[0][3], " CALLED BY ",inspect.stack()[1][3])
    #print("@processTrigger: ",triggerType)

    updateGlobalSettings()

    logger("_INFO_", "Trigger type:", triggerType)
    if(triggerType == TriggerType.MOTION):
        if(isMotionTriggerActive() == True):
            processMotionTrigger(triggerType="motion")
        else:
            logger("_INFO_", "Motion triggers are disabled in appSettings. Ignoring")
    elif(triggerType == TriggerType.ON_DEMAND_SOLO):
        processMotionTrigger(triggerType="solo")
    elif(triggerType == TriggerType.ON_DEMAND_SYMPHONY):
        processMotionTrigger(triggerType="symphony")        
    elif(triggerType == TriggerType.ALARM):
        print("process alarm")
    else:
        print("unknown trigger type: ", triggerType)


if __name__ == "__main__":
    print("Error: Interface.py cannot be executed as a standalone python program")