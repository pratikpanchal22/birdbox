import MySQLdb
import random

def getData():
    db = MySQLdb.connect("localhost", "user", "password", "temps")
    curs=db.cursor()

    curs.execute ("SELECT * FROM tempdat")

    print ("\nDate         Time           Zone         Temperature")
    print ("===========================================================")

    data = 0
    for reading in curs.fetchall():
        print(str(reading[0])," ",str(reading[1]),"     ",reading[2],"    ",str(reading[3]))
        data = reading[3]

    db.close()

    return data