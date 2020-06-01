import os
import random
from enum import Enum
from threading import Thread, current_thread
import inspect
import json
from dateutil import parser
import datetime
import time
#
from common.audio_interface import AudioThread as at
from common.audio_interface import AlsaVolume as av
from common.utility import logger
from models import dbConfig as dbc
from models.data import Models
from models.data import ModelType
from models.database import Db
from interface.app_settings import AppSettings

#TRIGGER TYPES
class TriggerType(Enum):
    UNSUPPORTED_TRIGGER = 0
    MOTION = 1
    BUTTON_PRESS = 2
    ON_DEMAND_SOLO = 3
    ON_DEMAND_SYMPHONY = 4
    ALARM = 5

#CANDIDATE SELECTION MODELS
class CandidateSelectionModels(Enum):
    RNDM_TOP_75PC = 1   #Random candidate from top 75% of set that was sorted by last updated time with oldest on top

#GLOBALS - TODO: Move to persistent storage
randomizeNumberOfChannels = True #TODO: get this from settings
appSettings = ""
ambientAudioChannel1 = None
ambientAudioChannel2 = None
candidateAudioThreads = []

########################################################
##########  ~~~ GET CANDIDATE AUDIO FILES ~~~ ##########
########################################################
def getCandidateAudioFiles(appSettings, **kwargs):
    #print("\n--> ",inspect.stack()[0][3], " CALLED BY ",inspect.stack()[1][3])

    #TODO: Right now don't see any need to push motion events in db. So skipping. 
    #But if required, this will be the place to do so. 
    
    #2. TODO: Verify that required time has passed since last playback
    
    #Purge dead entries
    #Fetch
    activeEntries = Models(Db(dbc.MYSQL_DB).connection()).fetch(ModelType.ACTIVE_ENTRIES)
    activeEntries = [d[dbc.KEY_ID] for d in activeEntries]

    #3. Verify that number of active entries don't exceed maximum allowed
    if(len(activeEntries) > 0):
        purged = purgeDeadEntries(60)
        if(purged > 0):
            logger("_INFO_", purged, "Entries purged")
            activeEntries = Models(Db(dbc.MYSQL_DB).connection()).fetch(ModelType.ACTIVE_ENTRIES)

    logger("_INFO_", "Active entries:", activeEntries)
    logger("_INFO_", "Active/maxAllowed=", len(activeEntries), "/", appSettings.maxNumberOfAllowedSimultaneousChannels())
    if(len(activeEntries) >= appSettings.maxNumberOfAllowedSimultaneousChannels()):
        logger ("_INFO_", "Ignoring trigger. Exiting\n")
        return []

    #4. Compute number of channels to implement
    if (kwargs.get("triggerType") == "solo"):
        numberOfChannels = 1
    elif (kwargs.get("triggerType") == "symphony"):         
        numberOfChannels = appSettings.maxNumberOfAllowedSimultaneousChannels() - len(activeEntries)
    elif (kwargs.get("triggerType") == "motion"):
        if(randomizeNumberOfChannels):
            numberOfChannels = random.randint(1, appSettings.maxNumberOfAllowedSimultaneousChannels()-len(activeEntries))
        else:
            numberOfChannels = appSettings.maxNumberOfAllowedSimultaneousChannels() - len(activeEntries)
    else:
        return []
    
    #candidates = getCandidateAudioFiles(CandidateSelectionModels.RNDM_TOP_75PC, appSettings, numberOfChannels)
    if(numberOfChannels == 0):
        return []
    
    #Scope: 
    # (1) Fetch all sorted by last_updated asc
    data = Models(Db(dbc.MYSQL_DB).connection()).fetch(ModelType.IDS_NAMES_AUDIOFILE_SORTED_BY_LAST_UPDATED_OLDEST_FIRST)
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
        logger("INFO_", "Limit to same species: ", appSettings.isBirdChoiceLimitedToSameSpecies())
        if(appSettings.isBirdChoiceLimitedToSameSpecies()):
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
    

def purgeDeadEntries(seconds):
    return int(Models(Db(dbc.MYSQL_DB).connection()).push(ModelType.UNSET_ACTIVE_FOR_DEAD_ENTRIES, seconds))

def getAudioBasePath():
    cwd = os.getcwd()
    if cwd.endswith("/birdbox"):
        cwd += "/application"
    
    if cwd.endswith("/application"):
        cwd += "/static/sounds/"
        return cwd

    return ""   

####################################################################################
def isLightRingActivated():
    # TODO: Fetch relevant setting
    # Right now returning back motion enabled boolean
    return AppSettings().isMotionTriggerActive()

def processTrigger(triggerType):
    #logger("_INFO_", "\n--> ",inspect.stack()[0][3], " CALLED BY ",inspect.stack()[1][3])
    #print("@processTrigger: ",triggerType)

    c = []
    latestSettings = AppSettings()

    logger("_INFO_", "Trigger type:", triggerType)
    if(triggerType == TriggerType.MOTION):
        #1. Verify that triggers are enabled
        if(latestSettings.isMotionTriggerActive() == False):
            logger("_INFO_", "Motion triggers are disabled in appSettings. Exiting")
            return 
        #2. Verify that not in silent period
        if(latestSettings.isSilentPeriodActive()):
            logger("_INFO_", "Silent period active. Exiting")
            return 

        c = getCandidateAudioFiles(latestSettings, triggerType="motion")

    elif(triggerType == TriggerType.ON_DEMAND_SOLO):
        c = getCandidateAudioFiles(latestSettings, triggerType="solo")
    elif(triggerType == TriggerType.ON_DEMAND_SYMPHONY):
        c = getCandidateAudioFiles(latestSettings, triggerType="symphony")        
    elif(triggerType == TriggerType.ALARM):
        print("process alarm")
    elif(triggerType == TriggerType.BUTTON_PRESS):
        c = getCandidateAudioFiles(latestSettings, triggerType="solo")
    else:
        print("unknown trigger type: ", triggerType)
        return

    #Once we have candidates, start audio threads here
    for item in c:
        logger("_INFO_", "candidate item: ", item)
        adi = AudioDbInterface(item[dbc.KEY_ID], item[dbc.KEY_AUDIO_FILE])
        adi.start()

    return

##############################################################################
# This handler is called whenever saveSettings is called from client
##############################################################################
def settingsChangeHandler():
    global ambientAudioChannel1, ambientAudioChannel2

    latestSettings = AppSettings()
    logger("_INFO_", "\nLatest settings: id=", str(latestSettings.getId()))

    previousSettings = AppSettings(id=latestSettings.getId()-1)
    logger("_INFO_", "Previous settings: id=", previousSettings.getId())

    sNew = latestSettings.getSettings()
    sOld = previousSettings.getSettings()
    logger("_INFO_", "\n    ### Current Settings: ", sNew)
    logger("_INFO_", "\n    ### Previous Settings: ", sOld)

    #Ambient Sounscape handler
    for ambience in ['ambience1', 'ambience2']:
        ambientAudioChannel = ""
        if(ambience == 'ambience1'): 
            ambientAudioChannel = 'ambientAudioChannel1'
            ambientVolume = 'amb1Vol'
        elif(ambience == 'ambience2'):
            ambientAudioChannel = 'ambientAudioChannel2'
            ambientVolume = 'amb2Vol'
        else:
            continue

        #Case 1: Continuous playback/upstage was turned OFF
        if((sNew['continuousPlayback']['enabled'] == False or sNew['continuousPlayback']['upStageEnabled'] == False) and
            (sOld['continuousPlayback']['enabled'] == True and sOld['continuousPlayback']['upStageEnabled'] == True)):
            #processUpstageSoundscape(ambientAudioChannel, terminate=True)
            t = Thread(target=processUpstageSoundscape, args=(ambientAudioChannel,), kwargs={'terminate':True})
            t.start()
            continue

        #Case 2: Continuous playback/upstage was turned ON or MODIFIED or UNMODIFIED
        elif(sNew['continuousPlayback']['enabled'] == True and sNew['continuousPlayback']['upStageEnabled'] == True):
            #Collect new settings into a dictionary:
            
            newAtSettings = {
                'name': sNew['continuousPlayback'][ambience],
                'endTime': sNew['continuousPlayback']['endTime'],
                'vol' : sNew['continuousPlayback'][ambientVolume]
            }
            #processUpstageSoundscape(ambientAudioChannel, **newAtSettings)
            t = Thread(target=processUpstageSoundscape, args=(ambientAudioChannel,), kwargs={**newAtSettings})
            t.start()

    #Master Volume Handler
    if(sNew['volume'] != sOld['volume']):
        av.setVolume(int(sNew['volume']))

    #Continuous playback handler - birds
    #Case 1: Cp/birds was turned off
    if((sNew['continuousPlayback']['enabled'] == False or sNew['continuousPlayback']['birdsEnabled'] == False) and
       (sOld['continuousPlayback']['enabled'] == True and sOld['continuousPlayback']['birdsEnabled'] == True)):
       logger("_INFO_", "Cp/birds was turned OFF - will be handled automatically")

    #Case 2: Cp/birds was turned ON 
    elif((sNew['continuousPlayback']['enabled'] == True and sNew['continuousPlayback']['birdsEnabled'] == True) and
       (sOld['continuousPlayback']['enabled'] == False or sOld['continuousPlayback']['birdsEnabled'] == False)):
        logger("_INFO_", "Cp/birds was turned ON")
        t = Thread(target=continousPbBirdsThreadEmulation)
        t.start()

    #Case 3: Cp/birds unchanged
    else: 
        logger("_INFO_", "Cp/birds setting unchanged")

    return

def continousPbBirdsThreadEmulation(**kwargs):
    global candidateAudioThreads

    s = AppSettings()
    repeat = True
    while (repeat == True):

        if(s.isContinousPbBirdsEnabled() == False):
            #kill all audioThreads
            for a in candidateAudioThreads:
                a.terminate()
            
            logger("_INFO_", "Audio threads stopped. Exiting")
            repeat = False
            continue

        logger("_INFO_", "AudioThreads: Live: ", str(len(candidateAudioThreads)), "  Max Allowed:", str(s.maxNumberOfAllowedSimultaneousChannels()))
        if(len(candidateAudioThreads) < s.maxNumberOfAllowedSimultaneousChannels()):
            c = getCandidateAudioFiles(s, triggerType="solo")
            for item in c:
                logger("_INFO_", "candidate item: ", item)
                adi = AudioDbInterface(item[dbc.KEY_ID], item[dbc.KEY_AUDIO_FILE])
                adi.start()

        time.sleep(5)
        logger("_INFO_", "Checking if cb/birds is still active")
        s.refresh()
    
    return

def processUpstageSoundscape(ch, **kwargs):
    try:
        if(kwargs['terminate']):
            if(kwargs.get("terminate") == True):
                terminateSoundscapeAudioThread(ch)
        return
    except KeyError:
        logger("_INFO_", ch," won't be terminated")
    
    atSettings = {}
    for key, value in kwargs.items():
        if(key == 'name'):
            if(value == 'None'):
                terminateSoundscapeAudioThread(ch)
                return
            else:
                d = Models(Db(dbc.MYSQL_DB).connection()).fetch(ModelType.ID_FILE_FOR_NAME, value)[0]
                atSettings['fp'] = getAudioBasePath()+d[dbc.KEY_AUDIO_FILE]
        elif(key == 'endTime'):
            atSettings['terminateAt'] = value
        elif(key == 'vol'):
            atSettings['vol'] = value
        else:
            print("Unsupported key/value pair: ", str(key), ":", str(value))

    if(globals()[ch] == None or globals()[ch].isAlive() == False):
        #start new
        globals()[ch] = at(**atSettings) 
        globals()[ch].start()

        #Update database if required
        logger("_INFO_", "audiothread started and waiting for completion")

        #Wait for completion
        globals()[ch].join()

        #Update database: appSettings
        logger("_INFO_", "Update appSettings here to reflect thread termination")
        disableAmbientChannelAndUpdateSettings(ch)
    else:
        #update existing
        for k, v in atSettings.items():
            if(k=='fp'):
                try:
                    globals()[ch].changeFile(v)
                except:
                    logger("_ERROR_", "Fatal error: Could not change ", k, "on", ch)
            elif(k=='vol'):
                try:
                    globals()[ch].changeVolume(v)
                except:
                    logger("_ERROR_", "Fatal error: Could not change ", k, "on", ch)
            elif(k=='terminateAt'):
                try:
                    globals()[ch].setFutureTerminationTime(v)
                except:
                    logger("_ERROR_", "Fatal error: Could not change ", k, "on", ch)
            else:
                print("Unsupported AT key/value pair: ", str(k), ":", str(v))

    return

def terminateSoundscapeAudioThread(audioThread):
    if(globals()[audioThread] != None and globals()[audioThread].isAlive() == True):
        globals()[audioThread].terminate()
        globals()[audioThread] = None
    return

def disableAmbientChannelAndUpdateSettings(ch):
    
    if(ch == 'ambientAudioChannel1'):
        queryFrag = "'$.continuousPlayback.ambience1', 'None'"
    elif(ch == 'ambientAudioChannel2'):
        queryFrag = "'$.continuousPlayback.ambience2', 'None'"
    else:
        logger("_INFO_", "Unsupported channel: ", ch)
        return

    #Update app settings in-place
    a = Models(Db(dbc.MYSQL_DB).connection()).push(ModelType.UPDATE_APP_SETTINGS_IN_PLACE, str(queryFrag))
    logger("_INFO_", "Settings updated inplace in database. Return: ", str(a))
    return

###################################################################################
class AudioDbInterface(Thread):
    def __init__(self, id, audioFileName):
        Thread.__init__(self)

        self._id = id
        self._audioFileName = audioFileName
        return

    def run(self):
        global candidateAudioThreads

        atSettings = {}
        atSettings['fp'] = getAudioBasePath()+self._audioFileName
        atSettings['vol'] = 100
        atSettings['repeat'] = False
        atSettings['tName'] = "AudioThread_id_" + str(self._id)
        audioThread = at(**atSettings)

        #Use Id to mark entry as active
        Models(Db(dbc.MYSQL_DB).connection()).push(ModelType.FOR_ID_SET_ACTIVE_UPDATE_TS, self._id)

        #Start audio thread
        audioThread.start()

        candidateAudioThreads.append(audioThread)

        logger("_INFO_", "  Starting thread: ", audioThread.getName(), "  state=", audioThread.isAlive())

        #Wait for completion
        audioThread.join()

        #Use Id to mark entry as inactive
        Models(Db(dbc.MYSQL_DB).connection()).push(ModelType.FOR_ID_UNSET_ACTIVE, self._id)

        candidateAudioThreads.remove(audioThread)

        logger("_INFO_", "  Thread ending: ", audioThread.getName(), "  state=", audioThread.isAlive())
        return
###################################################################################

if __name__ == "__main__":
    print("Error: Interface.py cannot be executed as a standalone python program")