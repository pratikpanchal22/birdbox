import os
import random
import models as models
from enum import Enum
from threading import Thread
import inspect

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
maxNumberOfChannels = 5 #TODO: get this from settings
limitToSameSpecies = True #TODO: get this from settings    

def processMotionTrigger():
    print("\n--> ",inspect.stack()[0][3], " CALLED BY ",inspect.stack()[1][3])
    #TODO: Right now don't see any need to push motion events in db. So skipping. 
    #But if required, this will be the place to do so. 

    #Validations
    #1. TODO: Verify that not in silent period
    #2. TODO: Verify that required time has passed since last playback
    #2. Verify that no entry is active

    #Purge dead entries
    
    #Fetch
    activeEntries = models.fetchModel(models.ModelType.ACTIVE_ENTRIES)

    if(len(activeEntries) > 0):
        purged = purgeDeadEntries(60) 
        print("#################### Number OF ENTRIES PURGED: ",purged)
        if(purged > 0):
            activeEntries = models.fetchModel(models.ModelType.ACTIVE_ENTRIES)

    print ("\n~~~ Active=",len(activeEntries),"  :::  maxAllowed=",maxNumberOfChannels)
    if(len(activeEntries) >= maxNumberOfChannels):
        print ("Ignoring trigger.")
        return

    numberOfChannels = 1
    if(randomizeNumberOfChannels):
        numberOfChannels = random.randint(1, maxNumberOfChannels-len(activeEntries))
    else:
        numberOfChannels = maxNumberOfChannels - len(activeEntries)

    candidates = getCandidateAudioFiles(CandidateSelectionModels.RNDM_TOP_75PC, numberOfChannels)
    
    print("Candidate audio files:")
    for c in candidates:
        print ("\n~~~Requesting: ",c[2], " id=",c[0])
        Thread(target=executeAudioFileOnSeparateThread, args=[c[0], c[2]]).start()

    #osCmd = "python3 application/playAudioFileDbIntegration.py"
    #print("Invoking: ",osCmd)
    #os.system(osCmd)
    return

def purgeDeadEntries(seconds):    
    return int(models.fetchModel(models.ModelType.UNSET_ACTIVE_FOR_DEAD_ENTRIES, seconds))

def executeAudioFileOnSeparateThread(id, file):
    print("\n--> ",inspect.stack()[0][3], " CALLED BY ",inspect.stack()[1][3])
    #Use Id to mark entry as active
    models.fetchModel(models.ModelType.FOR_ID_SET_ACTIVE_UPDATE_TS, id)
    print("\nId: ",id, " marked as active")

    #Run audio file
    #audioCmd = "mpg321 --gain 10 --verbose "
    audioCmd = "mpg321 --gain 20 "
    basePath = "application/static/sounds/"
    osCmd = audioCmd + basePath + file
    print(" os.command: ",osCmd)
    os.system(osCmd)
    
    #Use Id to mark entry as inactive
    models.fetchModel(models.ModelType.FOR_ID_UNSET_ACTIVE, id)
    print("#### end of executeAudioFileOnSeparateThread for ", file)
    return    

def getCandidateAudioFiles(modelType, numberOfChannels):
    print("\n--> ",inspect.stack()[0][3], " CALLED BY ",inspect.stack()[1][3])
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

    print("Length: ",len(data))    
    eligibleLength = int(0.75 * len(data))
    candidates = []
    candidates.append(data[random.randint(0, eligibleLength-1)])
    data.remove(candidates[0])

    print("Number of channels to implement: ", numberOfChannels)

    speciesConstrainedSet = []
    #speciesConstrainedSet.append(candidates[0])
    if(limitToSameSpecies):
        for d in data:
            if(d == candidates[0]):
                print(d," already exists. Skipping")
                #data.remove(candidates[0])
                continue
            elif(d[1] == candidates[0][1]):
                speciesConstrainedSet.append(d)
        data = speciesConstrainedSet

    #At this point data is a curated set that does not contain the cadidates[0]
    print("Species constrained set: ", speciesConstrainedSet)
    print("Size of species constrained set: ", len(speciesConstrainedSet))

    if(numberOfChannels > 1):
        if(numberOfChannels > len(data)):
            print("Number of channels is more than data set at hand")
            for d in data:
                candidates.append(d)
        else:
            for i in range(0, numberOfChannels-1):
                print("\n Selecting channel: ",i+1)
                randomlyChosenRowIdx = random.randint(0,len(data)-1)
                print("Size of data: ",len(data), "  Chosen idx: ",randomlyChosenRowIdx)
                candidates.append(data[randomlyChosenRowIdx])
                #remove that row to avoid duplication
                data.remove(data[randomlyChosenRowIdx])

    print ("Final candidate list: ")
    #candidateAudioFiles = []
    #for c in candidates:
    #    print (c)
    #    candidateAudioFiles.append(c[1])
    
    return candidates

def playAudioFile(fileName):
    #Scope 
    # 1. Mark as active
    # 2. play file (threaded call)
    # 3. 
    return


def processTrigger(triggerType):
    print("\n--> ",inspect.stack()[0][3], " CALLED BY ",inspect.stack()[1][3])
    print("@processTrigger: ",triggerType)
    if(triggerType == TriggerType.MOTION):
        processMotionTrigger()
    elif(triggerType == TriggerType.ON_DEMAND):
        print("process onDemand")
    elif(triggerType == TriggerType.ALARM):
        print("process alarm")
    else:
        print("unknown trigger type: ", triggerType)