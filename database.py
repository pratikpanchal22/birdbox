import MySQLdb
import random

db = MySQLdb.connect("localhost", "user", "password", "temps")
curs=db.cursor()

query = "INSERT INTO tempdat values(CURRENT_DATE() - INTERVAL "+str(random.randint(0,1024))+" DAY, NOW(), 'kitchen', "+str(random.randint(0,1024))+")"
print("Database query: ",query)

try:
    #curs.execute ("INSERT INTO tempdat values(CURRENT_DATE() - INTERVAL ",random.randint(1,100)," DAY, NOW(), 'kitchen', ",random.randint(0,100),")")
    curs.execute(query)
    db.commit()
    print ("New Data committed")

except:
    print ("Error: the database is being rolled back")
    db.rollback()

curs.execute ("SELECT * FROM tempdat")

print ("\nDate         Time           Zone         Temperature")
print ("===========================================================")

for reading in curs.fetchall():
    print(str(reading[0])," ",str(reading[1]),"     ",reading[2],"    ",str(reading[3]))

db.close()