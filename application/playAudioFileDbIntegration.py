import os
import random
import time
import MySQLdb
import dbConfig

TABLE_NAME = "birdboxTable"

def getCandidateRowId(db, tableName):
    #Query to get all rows sorted by last_invoked ascending (oldest first) 
    query = "SELECT id FROM "+tableName+" ORDER BY last_invoked ASC;"
    cursor = db.cursor()
    cursor.execute(query)

    #List comprehensions
    ids = [item[0] for item in cursor.fetchall()]
    print(ids)

    eligibleLength = int(0.8 * len(ids))
    print("Eligibile length: ",eligibleLength)
    chosenId = ids[random.randint(0, eligibleLength-1)]
    #print("Chosen index: ", chosenId)
    
    cursor.close()
    return chosenId

def getAudioFilePathForRowId(db, tableName, candidateRowId):
    #Query to get audio file path for id
    query = "SELECT audio_file FROM "+tableName+" WHERE id = "+str(candidateRowId)+";"
    cursor = db.cursor()
    cursor.execute(query)

    filePath = [item[0] for item in cursor.fetchall()]
    #print(filePath[0])

    cursor.close()
    return filePath[0]

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
#######################################

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

query_useDb    = "USE "+dbConfig.MYSQL_DB+";"

cursor = db.cursor()
cursor.execute(query_useDb)
cursor.close()

candidateRowId = getCandidateRowId(db, TABLE_NAME)
print("Row Id to execute: ", candidateRowId)

#Get Audio file
audioFilePath = getAudioFilePathForRowId(db, TABLE_NAME, candidateRowId)
print("Audio file to execute: ", audioFilePath)

#Update last_invoked and mark as active=true
updateTsAndActivate(db, TABLE_NAME, candidateRowId)

#Execute audio file
print("Called from current working dir: ",os.getcwd())
basePath = "application/static/sounds/"
osCmd = "mpg321 --gain 10 --verbose " + basePath + audioFilePath
print(" os.command: ",osCmd)
#Simulate for now
#time.sleep(15)
os.system(osCmd)

#mark active = false
deactivateRow(db, TABLE_NAME, candidateRowId)

db.close()
exit()