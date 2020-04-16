from flask import Flask, render_template
#import fetchAllData
from flask_mysqldb import MySQL
#import MySQLdb

#import mysql.connector as connector
import datetime

app = Flask(__name__)

app.config['MYSQL_USER'] = 'user'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'temps'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)



@app.route("/")
def index():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M:%S")

    cursor = mysql.connection.cursor()
    #cursor.execute('CREATE TABLE example (id INTEGER, name VARCHAR(20))')

    cursor.execute('SELECT * FROM tempdat')
    
    #return str(results[5]['temperature'])
    row_headers=[x[0] for x in cursor.description]
    results = cursor.fetchall()

    json = []
    for result in results:
        json.append(dict(zip(row_headers,result)))

    templateData = {
        'dName' : 'Meadow Larks',
        'dImg': 'baldEagle.jpg',
        'dDesc' : 'The entropy of the universe increases with time. The total amount of free energy available for useful work decreases as time progresses.',
        'dPlace' : 'M384 Galaxy',
        'dAuthor' : 'Fellow Trooper',
        'dDate' : timeString
    }
    return render_template('index.html', **templateData)

@app.route("/temps")
def temps():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")

    cursor = mysql.connection.cursor()
    #cursor.execute('CREATE TABLE example (id INTEGER, name VARCHAR(20))')

    cursor.execute('SELECT * FROM tempdat')
    
    #return str(results[5]['temperature'])
    row_headers=[x[0] for x in cursor.description]
    results = cursor.fetchall()

    json = []
    for result in results:
        json.append(dict(zip(row_headers,result)))

    templateData = {
        'title' : 'HELLO!',
        'time': timeString,
        'var1' : str(json)
    }
    return render_template('index.html', **templateData)    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)