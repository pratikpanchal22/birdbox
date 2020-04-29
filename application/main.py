from flask import Flask, render_template, jsonify, request
from flask_mysqldb import MySQL
import os
from threading import Thread
import dbConfig as dbc
import datetime
import time
import json
from json import JSONEncoder
import interface as interface
import utilities as u

app = Flask(__name__)

app.config['MYSQL_USER'] = dbc.MYSQL_USER
app.config['MYSQL_PASSWORD'] = dbc.MYSQL_PASSWORD
app.config['MYSQL_HOST'] = dbc.MYSQL_HOST
app.config['MYSQL_DB'] = dbc.MYSQL_DB
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

#################### App Models #######################
def fetchActiveEntries():
    cursor = mysql.connection.cursor()
    query = "SELECT "+dbc.KEY_ID+" FROM birdboxTable where "+dbc.KEY_ACTIVE+" = true;"
    cursor.execute(query)
    return list(cursor.fetchall())

def fetchOnStageMetadata(comma_separated_ids):
    cursor = mysql.connection.cursor()
    #query = "SELECT "+dbc.KEY_ID+", "+dbc.KEY_NAME+", "+dbc.KEY_AUDIO_FILE+", "+dbc.KEY_AUDIO_TYPE+", "+dbc.KEY_DESCRIPTION+", "+dbc.KEY_DURATION+", "+dbc.KEY_CREDIT+", "+dbc.KEY_DATE_CREATED_OR_CAPTURED+", "+dbc.KEY_IMAGE_FILE+", "+dbc.KEY_IMAGE_DESC+", "+dbc.KEY_LOCATION+", "+dbc.KEY_URL+" "+" FROM birdboxTable where "+dbc.KEY_ACTIVE+" = true;"
    query = "SELECT "+dbc.KEY_ID+", "+dbc.KEY_NAME+", "+dbc.KEY_IMAGE_FILE+" "+" FROM birdboxTable where "+dbc.KEY_ID+" in (" + comma_separated_ids + ");"
    print("\n\n querY:",query)
    cursor.execute(query)
    return list(cursor.fetchall())

def fetchInfoForId(id):
    cursor = mysql.connection.cursor()
    query = "SELECT "+dbc.KEY_ID+", "+dbc.KEY_NAME+", "+dbc.KEY_AUDIO_FILE+", "+dbc.KEY_AUDIO_TYPE+", "+dbc.KEY_DESCRIPTION+", "+dbc.KEY_DURATION+", "+dbc.KEY_CREDIT+", "+dbc.KEY_DATE_CREATED_OR_CAPTURED+", "+dbc.KEY_IMAGE_FILE+", "+dbc.KEY_IMAGE_DESC+", "+dbc.KEY_LOCATION+", "+dbc.KEY_URL+" "+" FROM birdboxTable where "+dbc.KEY_ID+" = " + str(id)+";"
    cursor.execute(query)
    return list(cursor.fetchall())    

#################### App Routes ########################
@app.route("/")
@app.route("/index.htm")
@app.route("/index.html")
def index():
    ts = str(int(time.time()))

    jsInclude = '<script src="/static/js/scripts.js?t='+ts+'"></script>'
    cssInclude = '<link rel="stylesheet" href="static/css/styles.css?t='+ts+'">'
    
    templateData = {
        'jsInclude' : jsInclude,
        'cssInclude' : cssInclude
    }
    return render_template('index.html', **templateData)

@app.route("/infoPage.html")
def infoPage():    
    #Grab the id from url parameters
    id = request.args.get("id")
    #Fetch model
    data = fetchInfoForId(id)

    #If the data returned is not exactly 1, go to home page
    if(len(data) != 1):
        return index()

    ts = str(int(time.time()))

    jsInclude = '<script src="/static/js/scripts.js?t='+ts+'"></script>'
    jsInclude += '<script src="/static/js/infoPageScripts.js?t='+ts+'"></script>'
    cssInclude = '<link rel="stylesheet" href="static/css/styles.css?t='+ts+'">'

    templateData = {
        'jsInclude' : jsInclude,
        'cssInclude' : cssInclude
    }

    templateData.update(data[0])

    #Pass to template Data
    return render_template('infoPage.html', **templateData)

@app.route("/settings.html")
def settings():
    ts = str(int(time.time()))

    jsInclude = '<script src="/static/js/scripts.js?t='+ts+'"></script>'
    jsInclude += '<script src="/static/js/settings.js?t='+ts+'"></script>'
    cssInclude = '<link rel="stylesheet" href="static/css/styles.css?t='+ts+'">'
    cssInclude += '<link rel="stylesheet" href="static/css/settings.css?t='+ts+'">'

    templateData = {
        'jsInclude' : jsInclude,
        'cssInclude' : cssInclude
    }

    return render_template('settings.html', **templateData)    

@app.route("/onDemand.json")
def onDemand():
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
    ts = str(int(time.time()))
    
    t = request.args.get("t")

    print("local ts=",ts," t=",t," diff=",int(ts)-int(t))

    jsonObj = {
        "state":"unknown",
        "ts":ts
    }

    if(int(ts) - int(t) > 2):
        #Request too old
        jsonObj["state"] = "request too old"
        print("Rejecting request because it is too old", jsonObj)
        return jsonify(jsonObj)

    entries = fetchActiveEntries()
    print("\n\nfetchActiveEntries: Converting entries to JSON:")
    entries = [e['id'] for e in entries]
    print(json.dumps(entries))

    if(len(entries)==0):
        jsonObj["state"] = "empty"
    else:
        jsonObj["state"] = "successful"
        jsonObj["data"] = json.dumps(entries)
        
    return json.dumps(jsonObj)

@app.route("/idData.json")
def idData():
    ts = str(int(time.time()))
    
    t = request.args.get("t")
    comma_separated_ids = request.args.get("id")
    #ids = u.comma_separated_params_to_list(request.args.get("id"))
    #print ("\n\n############# ids: ",ids)
    #for id in ids:
    #    print ("id: ",id)

    print("local ts=",ts," t=",t," diff=",int(ts)-int(t))

    jsonObj = {
        "state":"unknown",
        "ts":ts
    }

    if(int(ts) - int(t) > 2):
        #Request too old
        jsonObj["state"] = "request too old"
        print("Rejecting request because it is too old", jsonObj)
        return jsonify(jsonObj)

    entries = fetchOnStageMetadata(comma_separated_ids)
    print("\n\nConverting entries to JSON:")
    print(json.dumps(entries, cls=u.DateTimeEncoder))

    if(len(entries)==0):
        jsonObj["state"] = "empty"
    else:
        jsonObj["state"] = "successful"
        jsonObj["data"] = json.dumps(entries, cls=u.DateTimeEncoder)

    return json.dumps(jsonObj)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)