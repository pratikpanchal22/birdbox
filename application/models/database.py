import MySQLdb
import MySQLdb.cursors
#
from models import dbConfig as dbc

class Db:
    def __init__(self, database):
        self._dbName = database

    def connection(self):
        #CONNECT TO DATABASE
        db = ''
        for attempt in range(1):
            try:
                db = MySQLdb.connect(dbc.MYSQL_HOST, 
                                    dbc.MYSQL_USER, 
                                    dbc.MYSQL_PASSWORD, 
                                    self._dbName,
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

        query_useDb = "USE "+self._dbName+";"
        cursor = db.cursor()
        cursor.execute(query_useDb)
        cursor.close()
        return db