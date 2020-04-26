from flask import Flask, render_template, jsonify, request
from flask_mysqldb import MySQL
import os
from threading import Thread
import dbConfig as dbc
import datetime
import time
import interface as interface

app = Flask(__name__)

app.config['MYSQL_USER'] = dbc.MYSQL_USER
app.config['MYSQL_PASSWORD'] = dbc.MYSQL_PASSWORD
app.config['MYSQL_HOST'] = dbc.MYSQL_HOST
app.config['MYSQL_DB'] = dbc.MYSQL_DB
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

#################### App Models #######################
def fetchOnStageMetadata():
    cursor = mysql.connection.cursor()
    tableName = 'birdboxTable'
    query = "SELECT * FROM "+tableName+" where active = true;"
    cursor.execute(query)
    return cursor.fetchall()

#################### App Routes ########################
@app.route("/")
def index():
    now = datetime.datetime.now()
    ts = str(int(time.time()))
    #timeString = now.strftime("%Y-%m-%d %H:%M:%S")

    jsInclude = '<script src="/static/js/scripts.js?t='+ts+'"></script>'
    cssInclude = '<link rel="stylesheet" href="static/css/styles.css?t='+ts+'">'
    
    templateData = {
        'jsInclude' : jsInclude,
        'cssInclude' : cssInclude
    }
    return render_template('index.html', **templateData)

@app.route("/onDemand.json")
def onDemand():
    now = datetime.datetime.now()
    ts = str(int(time.time()))

    t = Thread(target=interface.processTrigger, args=[(interface.TriggerType.ON_DEMAND)])
    t.name = "thread_motion_"+str(ts)
    t.start()

    response = {
        "state":"successful",
        "ts": ts
    }

    return jsonify(response)

@app.route("/onStage.json")
def onStage():
    now = datetime.datetime.now()
    ts = str(int(time.time()))
    
    t = request.args.get("t")

    print("local ts=",ts," t=",t," diff=",int(ts)-int(t))

    json = {
        "state":"unknown",
        "ts":ts
    }

    if(int(ts) - int(t) > 2):
        #Request too old
        json["state"] = "request too old"
        print("Rejecting request because it is too old", json)
        return jsonify(json)

    entries = fetchOnStageMetadata()

    if(len(entries)==1):
        json["state"] = "successful"
        e = entries[0]
        json["id"] = e["id"]
        json["name"] = e["name"]
        json["audio_file"] = e["audio_file"]
        json["audio_type"] = e["audio_type"]
        json["description"] = e["description"]
        json["duration"] = e["duration"]
        json["credit"] = e["credit"]
        json["date_created_or_captured"] = e["date_created_or_captured"]
        json["image_file"] = e["image_file"]
        json["image_desc"] = e["image_desc"]
        json["location"] = e["location"]
        json["url"] = e["url"]
    elif(len(entries)==0):
        json["state"] = "empty"
    else:
        json["state"] = "multiple_entries"+str(len(entries))   
        
    return jsonify(json)

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