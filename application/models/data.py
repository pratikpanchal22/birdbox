from enum import Enum
#
from models import dbConfig as dbc
from common.utility import logger

#################### App Models #######################
#MODEL TYPES
class ModelType(Enum):
    UNINITIALIZED_MODEL_TYPE = 0
    #Fetch
    ACTIVE_ENTRIES = 1
    METADATA_FOR_IDS = 2
    INFO_FOR_ID = 3
    APP_SETTINGS = 4
    APP_SETTINGS_FOR_ID = 5
    LIST_OF_LOCATIONS = 6
    LIST_OF_SOUNDSCAPES_FOR_LOC = 7
    LOCATION_INFO = 8
    IDS_NAMES_AUDIOFILE_SORTED_BY_LAST_UPDATED_OLDEST_FIRST = 9
    ID_FILE_FOR_NAME = 10
    #Push
    UNSET_ACTIVE_FOR_DEAD_ENTRIES = 11
    FOR_ID_SET_ACTIVE_UPDATE_TS = 12
    FOR_ID_UNSET_ACTIVE = 13
    UPDATE_APP_SETTINGS_IN_PLACE = 14

class Models:
    def __init__(self, dbConn):
        self.dbConnection = dbConn
        self.modelType = ModelType.UNINITIALIZED_MODEL_TYPE
        self.query = ""
        
    def fetch(self, modelType, *argv):
        self.modelType = modelType
        
        if(self.modelType == ModelType.ACTIVE_ENTRIES):
            self.query = ("SELECT "+dbc.KEY_ID+" FROM birdboxTable WHERE ("
                              +dbc.KEY_ACTIVE+" = true AND "
                              +dbc.KEY_AUDIO_TYPE+" != '"
                              +dbc.KEY_AUDIO_TYPE_VAL_SOUNDSCAPE+"');")
        
        elif(self.modelType == ModelType.APP_SETTINGS):
            self.query = ("SELECT "+dbc.KEY_ID+", "+dbc.KEY_LAST_UPDATED+", "+dbc.KEY_SETTINGS+" "
                              +" FROM "+dbc.TABLE_SETTINGS+" ORDER BY "+dbc.KEY_ID+" DESC LIMIT 1;")
        
        elif(self.modelType == ModelType.APP_SETTINGS_FOR_ID):
            try:
                id = argv[0]
            except:
                print("ERROR: Expected id")
                return
            self.query = ("SELECT "+dbc.KEY_ID+", "+dbc.KEY_LAST_UPDATED+", "+dbc.KEY_SETTINGS+" "
                              +" FROM "+dbc.TABLE_SETTINGS
                              +" WHERE "+dbc.KEY_ID+" = " +str(id)+";")

        elif(self.modelType == ModelType.LIST_OF_LOCATIONS):
            self.query = "SELECT DISTINCT "+dbc.KEY_LOCATION+" from birdboxTable;"
        
        elif(self.modelType == ModelType.LIST_OF_SOUNDSCAPES_FOR_LOC):
            try:
                loc = argv[0]
            except:
                print("ERROR: Expected location")
                return
            self.query = "SELECT "+dbc.KEY_NAME+" from birdboxTable WHERE ("+dbc.KEY_AUDIO_TYPE+" = '"+dbc.KEY_AUDIO_TYPE_VAL_SOUNDSCAPE+"' AND "+dbc.KEY_LOCATION+" = '"+loc+"');"
        
        elif(self.modelType == ModelType.METADATA_FOR_IDS):
            try:
                comma_separated_ids = argv[0]
            except:
                print("ERROR: Expected comma_sep_values")
                return
            comma_separated_ids = argv[0]
            self.query = ("SELECT "+dbc.KEY_ID+", "+dbc.KEY_NAME+", "+dbc.KEY_IMAGE_FILE+" "
                                  +" FROM birdboxTable where "
                                  +dbc.KEY_ID+" in (" + comma_separated_ids + ");")
        
        elif(self.modelType == ModelType.INFO_FOR_ID):
            try:
                id = argv[0]
            except:
                print("ERROR: Expected id")
                return
            self.query = "SELECT "+dbc.KEY_ID+", "+dbc.KEY_NAME+", "+dbc.KEY_AUDIO_FILE+", "+dbc.KEY_AUDIO_TYPE+", "+dbc.KEY_DESCRIPTION+", "+dbc.KEY_DURATION+", "+dbc.KEY_CREDIT+", "+dbc.KEY_DATE_CREATED_OR_CAPTURED+", "+dbc.KEY_IMAGE_FILE+", "+dbc.KEY_IMAGE_DESC+", "+dbc.KEY_LOCATION+", "+dbc.KEY_URL+" "+" FROM birdboxTable where "+dbc.KEY_ID+" = " + str(id)+";"
        
        elif(self.modelType == ModelType.LOCATION_INFO):
            try:
                loc = argv[0]
            except:
                print("Error: Expected location")
                return
            self.query = ("SELECT COUNT(*) as total, "
                            + "(SELECT COUNT(distinct name) FROM birdboxTable WHERE audio_type != 'soundscape' and location = '"+str(loc)+"') as distinctBirds, "
                            + "(SELECT COUNT(distinct audio_file) FROM birdboxTable WHERE audio_type != 'soundscape' and location = '"+str(loc)+"') as totalBirdSounds, "
                            + "(SELECT COUNT(distinct audio_file) FROM birdboxTable WHERE audio_type = 'soundscape' and location = '"+str(loc)+"') as landscapeSounds "
                         +"FROM birdboxTable WHERE location = '"+str(loc)+"';")
        
        elif(self.modelType == ModelType.IDS_NAMES_AUDIOFILE_SORTED_BY_LAST_UPDATED_OLDEST_FIRST):
            self.query = ("SELECT "+dbc.KEY_ID+", "+dbc.KEY_NAME+", "+dbc.KEY_AUDIO_FILE
                            +" FROM birdboxTable WHERE "
                            +dbc.KEY_AUDIO_TYPE+" != 'soundscape' ORDER BY "+dbc.KEY_LAST_INVOKED+" ASC;")
        
        elif(self.modelType == ModelType.ID_FILE_FOR_NAME):
            try:
                name = argv[0]
            except:
                print("Error: Expected name")
                return
            self.query = ("SELECT "+dbc.KEY_ID+", "+dbc.KEY_AUDIO_FILE
                             +" FROM birdboxTable"
                             +" WHERE "+dbc.KEY_NAME+" = '"+str(name)+"';")

        else:
            print("ERROR: Unsupported model type for method:fetch : ",str(self.modelType))
            return
        
        if(self.query == ""):
            print("Error! Empty query / unsupported ModelType")
            return
        
        #logger("_INFO_", "Query: ", self.query)
        cursor = self.dbConnection.cursor()
        cursor.execute(self.query)
        r = list(cursor.fetchall())
        cursor.close()
        #self.dbConnection.connection.close()
        return r

    def push(self, modelType, *argv):
        self.modelType = modelType

        if(self.modelType == ModelType.APP_SETTINGS):
            try:
                s = argv[0]
            except:
                print("ERROR: Expected string of settings")
                return
            self.query = "INSERT INTO "+dbc.TABLE_SETTINGS+" ("+dbc.KEY_SETTINGS+") VALUES ('" + s + "');"

        elif(self.modelType == ModelType.UNSET_ACTIVE_FOR_DEAD_ENTRIES):
            try:
                seconds = argv[0]
            except:
                print("WARNING: Expected seconds offset. Defaulting to 10")
                seconds = 10

            self.query = ("UPDATE birdboxTable SET "+dbc.KEY_ACTIVE+" = false WHERE "
                            +dbc.KEY_ACTIVE+" = true AND UNIX_TIMESTAMP()-UNIX_TIMESTAMP("
                            +dbc.KEY_LAST_UPDATED+")>duration+"+str(seconds)+";")

        elif(self.modelType == ModelType.FOR_ID_SET_ACTIVE_UPDATE_TS):
            try:
                id = argv[0]
            except:
                print("ERROR: Expected id")
                return
            self.query = ("UPDATE birdboxTable SET "
                             +dbc.KEY_LAST_INVOKED+" = now(), "
                             +dbc.KEY_ACTIVE+" = true WHERE "
                             +dbc.KEY_ID+" = "+str(id)+";")

        elif(self.modelType == ModelType.FOR_ID_UNSET_ACTIVE):
            try:
                id = argv[0]
            except:
                print("ERROR: Expected id")
                return
            self.query = ("UPDATE birdboxTable SET "
                             +dbc.KEY_ACTIVE+" = false WHERE "
                             +dbc.KEY_ID+" = "+str(id)+";")

        elif(self.modelType == ModelType.UPDATE_APP_SETTINGS_IN_PLACE):
            try:
                s = argv[0]
            except:
                print("ERROR: Expected query fragment string")
                return
            self.query = ("UPDATE "+dbc.TABLE_SETTINGS
                            +" SET settings = JSON_SET(settings, "+s+")"
                            +" WHERE id = (SELECT max(id) FROM "+dbc.TABLE_SETTINGS+");")

        else:
            print("ERROR: Unsupported model type for method:push : ",str(self.modelType))
            return

        if(self.query == ""):
            print("Error! Empty query / unsupported ModelType")
            return

        cursor = self.dbConnection.cursor()
        results = cursor.execute(self.query)
        self.dbConnection.commit()
        cursor.close()
        return results