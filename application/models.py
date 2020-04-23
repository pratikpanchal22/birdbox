import datetime, time
import random
import MySQLdb
import dbConfig
from enum import Enum

#MODEL TYPES
class ModelType(Enum):
    ACTIVE_ENTRIES = 1
    ID_SORTED_BY_LAST_UPDATED_OLDEST_FIRST = 2
    IDS_NAMES_AUDIOFILE_SORTED_BY_LAST_UPDATED_OLDEST_FIRST = 3
    FOR_ID_SET_ACTIVE_UPDATE_TS = 4
    FOR_ID_UNSET_ACTIVE = 5
    UNSET_ACTIVE_FOR_DEAD_ENTRIES = 6

TABLE_NAME = "birdboxTable"

def connectToDatabase():
    #CONNECT TO DATABASE
    db = ''
    for attempt in range(1):
        try:
            db = MySQLdb.connect(dbConfig.MYSQL_HOST, dbConfig.MYSQL_USER, dbConfig.MYSQL_PASSWORD, dbConfig.MYSQL_DB)
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
            print("Connection to database established")
            break

    query_useDb = "USE "+dbConfig.MYSQL_DB+";"
    cursor = db.cursor()
    cursor.execute(query_useDb)
    cursor.close()
    return db

def getActiveEntriesFromDb(db, tableName):
    #Query to get all active rows
    query = "SELECT id FROM "+tableName+" WHERE active = true;"
    cursor = db.cursor()
    cursor.execute(query)
    results = [item[0] for item in cursor.fetchall()]
    cursor.close()
    return results

def getIdsSortedByLastUpdatedOldestFirst(db, tableName):
    #Query to get all rows sorted by last_invoked ascending (oldest first) 
    query = "SELECT id FROM "+tableName+" ORDER BY last_invoked ASC;"
    cursor = db.cursor()
    cursor.execute(query)
    #List comprehensions
    ids = [item[0] for item in cursor.fetchall()]
    cursor.close()
    return ids

def getQueryResultsAsArray(db, tableName, query):
    cursor = db.cursor()
    cursor.execute(query)
    results = list(cursor.fetchall())
    #print ("getQueryResultsAsArray: ",results)
    print("\ngetQueryResultsAsArray: ")

    #ids = [item[2] for item in results]
    #print (ids)

    cursor.close()
    return results        

def updateTsAndActivate(db, tableName, candidateRowId):
    #Query to update date time and set active flag
    query = "UPDATE "+tableName+" SET last_invoked = now(), active = true WHERE id = "+str(candidateRowId)+";"
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    cursor.close()
    return

def deactivateRow(db, tableName, candidateRowId):
    #Query to update date time and set active flag
    query = "UPDATE "+tableName+" SET active = false WHERE id = "+str(candidateRowId)+";"
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    cursor.close()
    return

def purgeDeadEntries(db, tableName, seconds):
    #Query to update date time and set active flag
    query = "UPDATE "+tableName+" SET active = false WHERE active = true AND UNIX_TIMESTAMP()-UNIX_TIMESTAMP(last_updated)>duration+"+str(seconds)+";"
    cursor = db.cursor()
    results = cursor.execute(query)
    print ("purgeDeadEntries: ", results)
    db.commit()
    cursor.close()
    return results

##############################################################
def fetchModel(modelType, *argv):
    if(modelType == ModelType.ACTIVE_ENTRIES):
        return getActiveEntriesFromDb(connectToDatabase(), TABLE_NAME)
    elif(modelType == ModelType.ID_SORTED_BY_LAST_UPDATED_OLDEST_FIRST):
        return getIdsSortedByLastUpdatedOldestFirst(connectToDatabase(), TABLE_NAME)
    elif(modelType == ModelType.IDS_NAMES_AUDIOFILE_SORTED_BY_LAST_UPDATED_OLDEST_FIRST):
        query = "SELECT id, name, audio_file, id FROM "+TABLE_NAME+" ORDER BY last_invoked ASC;"
        return getQueryResultsAsArray(connectToDatabase(), TABLE_NAME, query)
    elif(modelType == ModelType.FOR_ID_SET_ACTIVE_UPDATE_TS):
        return updateTsAndActivate(connectToDatabase(), TABLE_NAME, argv[0])
    elif(modelType == ModelType.FOR_ID_UNSET_ACTIVE):
        return deactivateRow(connectToDatabase(), TABLE_NAME, argv[0])    
    elif(modelType == ModelType.UNSET_ACTIVE_FOR_DEAD_ENTRIES):
        return purgeDeadEntries(connectToDatabase(), TABLE_NAME, argv[0])        
    else:
        print("[Models] Error! Unknown/unsupported model type: ", modelType)

    return