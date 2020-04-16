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
app.config['MYSQL_DB'] = 'birdbox'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)



@app.route("/")
def index():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M:%S")

    cursor = mysql.connection.cursor()

    tableName = 'birdboxTable'
    #query = "SELECT image_file, audio_file, name, description, location, author, organization, date_created_or_captured FROM "+tableName+" where active = true;"
    query = "SELECT * FROM "+tableName+" where active = true;"
    cursor.execute(query)
    
    #row_headers=[x[0] for x in cursor.description]

    entries = cursor.fetchall() #[item[0] for item in cursor.fetchall()]
    #TODO: Make sure this is always exactly 1
    print("Number of rows returned: ", len(entries))

    #for row in entry:
    #    print("{0} {1} {2} {3}\n".format(row["id"], row["last_updated"], row["audio_file"], row["date_created_or_captured"]))
    
    #while i<len(e):
    #    #print(col_names[i]," ",col_data_types[i],",")
    #    if(e[i] is None):
    #        e[i] = "empty"
    #    
    #    i+=1
    
    dOnStage = False
    dName = ''
    dImg = ''
    dAudio = ''
    dDesc = ''
    dPlace = ''
    dAuthor = ''
    dDate = ''
    dOrg = ''

    if len(entries) != 1:
        print("Error. Expected entry length is EXACTLY 1")
        dOnStage = False
    else:
        e = entries[0]
        print(e)
        dOnStage = True
        dName = e["name"]
        dImg = e["image_file"]
        dAudio = e["audio_file"]
        dDesc = e["description"]
        dPlace = e["location"]
        dAuthor = e["author"]
        dDate = e["date_created_or_captured"]
        dOrg = e["organization"]
    
    print("Item on stage: ",dOnStage)
    print("Image file: ",dImg)
    print("Audio file: ",dAudio)
    print("Name: ",dName)
    print("Description: ",dDesc)
    print("Location: ",dPlace)
    print("Author: ",dAuthor)
    print("Organization: ",dOrg)

    templateData = {
        'dOnStage' : dOnStage,
        'dName' : dName,
        'dImg': dImg,
        'dDesc' : dDesc,
        'dPlace' : dPlace,
        'dAuthor' : dAuthor,
        'dDate' : timeString,
        'dOrg' : dOrg
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