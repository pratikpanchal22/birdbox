import datetime, time
import random
import MySQLdb
import MySQLdb.cursors
import dbConfig as dbc
from enum import Enum

#MODEL TYPES
class ModelType(Enum):
    ACTIVE_ENTRIES = 1
    ID_SORTED_BY_LAST_UPDATED_OLDEST_FIRST = 2
    IDS_NAMES_AUDIOFILE_SORTED_BY_LAST_UPDATED_OLDEST_FIRST = 3
    FOR_ID_SET_ACTIVE_UPDATE_TS = 4
    FOR_ID_UNSET_ACTIVE = 5
    UNSET_ACTIVE_FOR_DEAD_ENTRIES = 6
    APP_SETTINGS = 7
    APP_SETTINGS_FOR_ID = 8
    ID_FILE_FOR_NAME = 9
    PUSH_APP_SETTINGS = 10

TABLE_NAME = "birdboxTable"

def connectToDatabase():
    #CONNECT TO DATABASE
    db = ''
    for attempt in range(1):
        try:
            db = MySQLdb.connect(dbc.MYSQL_HOST, 
                                 dbc.MYSQL_USER, 
                                 dbc.MYSQL_PASSWORD, 
                                 dbc.MYSQL_DB,
                                 cursorclass=MySQLdb.cursors.DictCursor)
        except MySQLdb._exceptions.OperationalError as err:
            print("Something went wrong: {}".format(err))
            print("Error code: ", err.args[0])
            print("Error: ", err.args[1])
            if(err.args[0] == 1049):
                print("Database schema does not exist. Exiting")
                exit()
                #createDatabase(dbConfig.MYSQL_DB)
                #db = MySQLdb.connect("localhost", "user", "password", "birdbox")
        else:
            #print("Connection to database established")
            break

    query_useDb = "USE "+dbc.MYSQL_DB+";"
    cursor = db.cursor()
    cursor.execute(query_useDb)
    cursor.close()
    return db

def getActiveEntriesFromDb(db, tableName):
    #Query to get all active rows
    query = "SELECT "+dbc.KEY_ID+" FROM "+tableName+" WHERE "+dbc.KEY_ACTIVE+" = true;"
    cursor = db.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

def getQueryResultsAsList(db, tableName, query):
    cursor = db.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return list(results)

##################################################
####### Models that require db.commit ############
##################################################

def performDbOperation(db, tableName, query):
    cursor = db.cursor()
    results = cursor.execute(query)
    db.commit()
    cursor.close()
    return results 

##############################################################
def fetchModel(modelType, *argv):

    dbConnection = connectToDatabase()

    if(modelType == ModelType.ACTIVE_ENTRIES):
        return getActiveEntriesFromDb(dbConnection, TABLE_NAME)
    
    elif(modelType == ModelType.IDS_NAMES_AUDIOFILE_SORTED_BY_LAST_UPDATED_OLDEST_FIRST):
        query = "SELECT "+dbc.KEY_ID+", "+dbc.KEY_NAME+", "+dbc.KEY_AUDIO_FILE+" FROM "+TABLE_NAME+" WHERE "+dbc.KEY_AUDIO_TYPE+" != 'soundscape' ORDER BY "+dbc.KEY_LAST_INVOKED+" ASC;"
        return getQueryResultsAsList(dbConnection, TABLE_NAME, query)
    
    elif(modelType == ModelType.FOR_ID_SET_ACTIVE_UPDATE_TS):
        query = "UPDATE "+TABLE_NAME+" SET "+dbc.KEY_LAST_INVOKED+" = now(), "+dbc.KEY_ACTIVE+" = true WHERE "+dbc.KEY_ID+" = "+str(argv[0])+";"
        return performDbOperation(dbConnection, TABLE_NAME, query)
    
    elif(modelType == ModelType.FOR_ID_UNSET_ACTIVE):   
        query = "UPDATE "+TABLE_NAME+" SET "+dbc.KEY_ACTIVE+" = false WHERE "+dbc.KEY_ID+" = "+str(argv[0])+";"
        return performDbOperation(dbConnection, TABLE_NAME, query)
    
    elif(modelType == ModelType.UNSET_ACTIVE_FOR_DEAD_ENTRIES):
        query = "UPDATE "+TABLE_NAME+" SET "+dbc.KEY_ACTIVE+" = false WHERE "+dbc.KEY_ACTIVE+" = true AND UNIX_TIMESTAMP()-UNIX_TIMESTAMP("+dbc.KEY_LAST_UPDATED+")>duration+"+str(argv[0])+";"
        return performDbOperation(dbConnection, TABLE_NAME, query)

    elif(modelType == ModelType.PUSH_APP_SETTINGS):
        try:
            s = argv[0]
        except:
            print("ERROR: Expected string of settings")
            return
        query = "INSERT INTO "+dbc.TABLE_SETTINGS+" ("+dbc.KEY_SETTINGS+") VALUES ('" + s + "');"
        return performDbOperation(dbConnection, TABLE_NAME, query)

    elif(modelType == ModelType.APP_SETTINGS):
        query = "SELECT "+dbc.KEY_ID+", "+dbc.KEY_LAST_UPDATED+", "+dbc.KEY_SETTINGS+" "+" FROM "+dbc.TABLE_SETTINGS+" ORDER BY "+dbc.KEY_ID+" DESC LIMIT 1;"
        return  getQueryResultsAsList(dbConnection, TABLE_NAME, query)

    elif(modelType == ModelType.APP_SETTINGS_FOR_ID):
        query = "SELECT "+dbc.KEY_ID+", "+dbc.KEY_LAST_UPDATED+", "+dbc.KEY_SETTINGS+" "+" FROM "+dbc.TABLE_SETTINGS+" WHERE "+dbc.KEY_ID+" = " +str(argv[0])+";"
        return  getQueryResultsAsList(dbConnection, TABLE_NAME, query)

    elif(modelType == ModelType.ID_FILE_FOR_NAME):
        query = "SELECT "+dbc.KEY_ID+", "+dbc.KEY_AUDIO_FILE+" FROM "+TABLE_NAME+" WHERE "+dbc.KEY_NAME+" = '"+str(argv[0])+"';"
        return getQueryResultsAsList(dbConnection, TABLE_NAME, query)

    else:
        print("[Models] Error! Unknown/unsupported model type: ", modelType)

    return