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

def getAudioAndImageFilePathsForRowId(db, tableName, candidateRowId):
    #Query to get audio file path for id
    query = "SELECT audio_file, image_file FROM "+tableName+" WHERE id = "+str(candidateRowId)+";"
    cursor = db.cursor()
    cursor.execute(query)

    results = cursor.fetchall()

    json = {}
    for x in results:
        json["audio_file"] = x[0]
        json["image_file"] = x[1]

    cursor.close()
    return json

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

def test(str):
    print("Invoked: ",str)
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

#Get Audio & Image file
json = getAudioAndImageFilePathsForRowId(db, TABLE_NAME, candidateRowId)
print(json)
audioFilePath = json["audio_file"]
imageFilePath = json["image_file"]

print("Audio file to execute: ", audioFilePath)
print("Image file to link: ", imageFilePath)

#Update last_invoked and mark as active=true
updateTsAndActivate(db, TABLE_NAME, candidateRowId)

#Link image file
stageImage = "application/static/images/stageImage.JPG"
osCmd = "rm "+stageImage+"; ln -s application/static/images/"+imageFilePath+" "+stageImage
print (osCmd)
os.system(osCmd)

#Execute audio file
#TODO
osCmd = "mpg321 --gain 100 --verbose " + audioFilePath
print("[SIMULATED] os.command: ",osCmd)
#Simulate for now
time.sleep(15)
#os.system(osCmd)

#mark active = false
deactivateRow(db, TABLE_NAME, candidateRowId)

db.close()
exit()