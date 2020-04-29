import os
import random
import models as models
from enum import Enum
from threading import Thread, current_thread
import inspect
from utilities import logger
import json
import dbConfig as dbc

#TRIGGER TYPES
class TriggerType(Enum):
    MOTION = 1
    ON_DEMAND = 2
    ALARM = 3 

#CANDIDATE SELECTION MODELS
class CandidateSelectionModels(Enum):
    RNDM_TOP_75PC = 1   #Random candidate from top 75% of set that was sorted by last updated time with oldest on top

#GLOBALS - TODO: Move to persistent storage
randomizeNumberOfChannels = True #TODO: get this from settings
maxNumberOfChannels = 5          #TODO: get this from settings
limitToSameSpecies = False       #TODO: get this from settings   
maxVolumeMotionTrigger = 20      #TODO: get this from settings   

def processMotionTrigger():
    #print("\n--> ",inspect.stack()[0][3], " CALLED BY ",inspect.stack()[1][3])
    
    #TODO: Right now don't see any need to push motion events in db. So skipping. 
    #But if required, this will be the place to do so. 

    #Validations
    #1. TODO: Verify that not in silent period
    #2. TODO: Verify that required time has passed since last playback
    
    #Purge dead entries
    #Fetch
    activeEntries = models.fetchModel(models.ModelType.ACTIVE_ENTRIES)
    activeEntries = [d[dbc.KEY_ID] for d in activeEntries]

    if(len(activeEntries) > 0):
        purged = purgeDeadEntries(60)
        if(purged > 0):
            logger("_INFO_", purged, "Entries purged")
            activeEntries = models.fetchModel(models.ModelType.ACTIVE_ENTRIES)

    logger("_INFO_", "Active entries:", activeEntries)
    logger("_INFO_", "Active/maxAllowed=", len(activeEntries), "/", maxNumberOfChannels)
    if(len(activeEntries) >= maxNumberOfChannels):
        logger ("_INFO_", "Ignoring trigger. Exiting\n")
        return

    numberOfChannels = 1
    if(randomizeNumberOfChannels):
        numberOfChannels = random.randint(1, maxNumberOfChannels-len(activeEntries))
    else:
        numberOfChannels = maxNumberOfChannels - len(activeEntries)

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
    audioCmd = "mpg321 --gain "+str(maxVolumeMotionTrigger)+" --quiet"
    basePath = " application/static/sounds/"
    osCmd = audioCmd + basePath + file
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
        logger("INFO_", "Limit to same species: ", limitToSameSpecies)
        if(limitToSameSpecies):
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
    
        if(numberOfChannels > len(data)):
            logger("_INFO_", "Number of channels is more than data set at hand")
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
    logger("_INFO_", "Trigger type:", triggerType)
    if(triggerType == TriggerType.MOTION):
        processMotionTrigger()
    elif(triggerType == TriggerType.ON_DEMAND):
        processMotionTrigger()
    elif(triggerType == TriggerType.ALARM):
        print("process alarm")
    else:
        print("unknown trigger type: ", triggerType)