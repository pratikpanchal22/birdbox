import json
from dateutil import parser
import datetime
#
from common.utility import logger
from models import dbConfig as dbc
from models.data import Models
from models.data import ModelType
from models.database import Db

class AppSettings:
    def __init__(self, **kwargs):
        try:
            self._appSettingsId = kwargs['id']
        except KeyError:
            self._appSettingsId = -1

        self.__fetchModel()    
        return

    def print(self):
        logger("_INFO_", "appSettings: id=", str(self._appSettings[0][dbc.KEY_ID]))
        logger("_INFO_", "appSettings: last updated=", str(self._appSettings[0][dbc.KEY_LAST_UPDATED]))
        logger("_INFO_", "appSettings: settings=", str(json.loads(self._appSettings[0][dbc.KEY_SETTINGS])))
        return

    def getId(self):
        return self._appSettings[0][dbc.KEY_ID]

    def getLastUpdated(self):
        return self._appSettings[0][dbc.KEY_LAST_UPDATED]

    def getSettings(self):
        return json.loads(self._appSettings[0][dbc.KEY_SETTINGS])

    def refresh(self):
        self.__fetchModel()
        return

    def save(self, jsonStr):
        Models(Db(dbc.MYSQL_DB).connection()).push(ModelType.APP_SETTINGS, jsonStr)
        self.refresh()
        return

    def __fetchModel(self):
        if(self._appSettingsId > 0):
            self._appSettings = Models(Db(dbc.MYSQL_DB).connection()).fetch(ModelType.APP_SETTINGS_FOR_ID, self._appSettingsId)
        else:
            self._appSettings = Models(Db(dbc.MYSQL_DB).connection()).fetch(ModelType.APP_SETTINGS)
        return

    def isMotionTriggerActive(self):
        #Default
        dv = True
        try:
            dv = self._appSettings[dbc.KEY_MOTION_TRIGGERS][dbc.KEY_ENABLED] 
        except:
            logger("_ERROR_", "appSettings[dbc.KEY_MOTION_TRIGGERS][dbc.KEY_ENABLED] doesn't exist")
        return dv

    def isSilentPeriodActive(self):
        dv = False
        try:
            silentPeriodEnabled = self._appSettings[dbc.KEY_SILENT_PERIOD][dbc.KEY_ENABLED]
            silentStartTime = parser.parse(self._appSettings[dbc.KEY_SILENT_PERIOD][dbc.KEY_START_TIME])
            silentEndTime = parser.parse(self._appSettings[dbc.KEY_SILENT_PERIOD][dbc.KEY_END_TIME])
        except:
            logger("_ERROR_", "appSettings doesn't exist")
            return dv

        if(silentPeriodEnabled == False):
            return False

        #Local time
        currentTime = datetime.datetime.now()
        logger("_INFO_","    ** silentStartTime = ", silentStartTime)
        logger("_INFO_","    ** currentTime = ", currentTime)
        logger("_INFO_","    ** silentEndTime = ", silentEndTime)
        
        if (silentStartTime < silentEndTime):
            if(silentStartTime <= currentTime < silentEndTime):
                dv = True
            else:
                dv = False
        elif (silentStartTime > silentEndTime):
            if(silentStartTime <= currentTime or currentTime < silentEndTime):
                dv = True
            else:
                dv = False
        else:
            if(silentStartTime == currentTime == silentEndTime):
                dv = True
            else:
                dv = False

        return dv

    def maxNumberOfAllowedSimultaneousChannels(self):
        #Default
        dv = 5
        try:
            dv = int(self._appSettings[dbc.KEY_SYMPHONY][dbc.KEY_MAXIMUM])
        except:
            logger("_ERROR_", "appSettings[dbc.KEY_SYMPHONY][dbc.KEY_MAXIMUM] doesn't exist")
        return dv

    def isBirdChoiceLimitedToSameSpecies(self):
        #Default
        dv = False
        try:
            dv = self._appSettings[dbc.KEY_SYMPHONY][dbc.KEY_LIMIT_TO_SAME_SPECIES] 
        except:
            logger("_ERROR_", "appSettings[dbc.KEY_SYMPHONY][dbc.KEY_LIMIT_TO_SAME_SPECIES] doesn't exist")
        return dv

    def maxVolume(self):
        #Default
        dv = 100
        try:
            dv = int(self._appSettings[dbc.KEY_VOLUME])
        except:
            logger("_ERROR_", "appSettings[dbc.KEY_VOLUME] doesn't exist")
        return dv

    def isContinuousPlaybackEnabled(self):
        return False

