#from importCsv import tableExists, createDatabase
import MySQLdb
import dbConfig
import json

TABLE_NAME = 'appSettings'

#CONNECT TO DATABASE
#TODO: Redundant - remove
db = ''
for attempt in range(2):
    try:
        db = MySQLdb.connect(dbConfig.MYSQL_HOST, dbConfig.MYSQL_USER, dbConfig.MYSQL_PASSWORD, dbConfig.MYSQL_DB)
    except MySQLdb._exceptions.OperationalError as err:
        print("Something went wrong: {}".format(err))
        print("Error code: ", err.args[0])
        print("Error: ", err.args[1])
        if(err.args[0] == 1049):
            print("Database schema does not exist.")
            #createDatabase(dbConfig.MYSQL_DB)
            #db = MySQLdb.connect("localhost", "user", "password", "birdbox")
            continue
    else:
        print("Connection to database established")
        break

#DROP TABLE IF TABLE EXISTS
#if(importCsv.tableExists(db, TABLE_NAME)):
#    cursor = db.cursor()
#    query = "DROP TABLE " + TABLE_NAME + ";"
#    cursor.execute(query)
#    cursor.close()

#TABLE EXISTS

#GET DATA
with open('factoryDefaultSettings.json') as f:
    data = json.load(f)

strJson = json.dumps(data)

#print("\nType of strJson: ", type(strJson))
print("factoryDefaultSettings.json: ", strJson)

query_useDb    = "USE birdbox;"
query_createTable1 = ("CREATE TABLE "+TABLE_NAME+" ( " +
                    "id INT NOT NULL UNIQUE AUTO_INCREMENT PRIMARY KEY, "+
                    "last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, "+
                    "settings JSON);")

query_populateTable1 = ('INSERT INTO appSettings (settings) ' +
                      'VALUES ('+
                      '\''+strJson+'\''
                      ');')

cursor = db.cursor()
cursor.execute(query_useDb)
cursor.execute(query_createTable1)
cursor.execute(query_populateTable1)
db.commit()
cursor.close()
db.close()