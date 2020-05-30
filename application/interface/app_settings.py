import json
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

