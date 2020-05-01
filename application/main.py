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
import ast

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

def fetchAppSettings():
    cursor = mysql.connection.cursor()
    query = "SELECT "+dbc.KEY_LAST_UPDATED+", "+dbc.KEY_SETTINGS+" "+" FROM "+dbc.TABLE_SETTINGS+" ORDER BY "+dbc.KEY_ID+" DESC LIMIT 1;"
    cursor.execute(query)
    return cursor.fetchall() 

def getLandscapeLocations():
    cursor = mysql.connection.cursor()
    query = "SELECT DISTINCT "+dbc.KEY_LOCATION+" from birdboxTable;"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results 

def updateAppSettings(s):
    conn=mysql.connection
    cursor = conn.cursor()
    query = "INSERT INTO "+dbc.TABLE_SETTINGS+" ("+dbc.KEY_SETTINGS+") VALUES ('" + s + "');"
    results = cursor.execute(query)
    conn.commit()
    print (results)
    return results


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

@app.route("/saveSettings.json", methods=['post', 'get'])
def saveSettings():

    #Get current copy of settings
    d = json.loads(list(fetchAppSettings())[0]['settings'])

    if(request.method == 'POST'):
        print("\n\n *********** form data ******************")
        print("request.data: ", request.data)
        print("request.form: ", request.form)
        if(request.form.get('cbSwitch')): print('cbSwitch checked')
        if(request.form.get('upstageSwitch')): print('upstageSwitch checked')
        if(request.form.get('mtEnabled')): print('mtEnabled checked')
        if(request.form.get('symphonySwitch')): print('symphonySwitch checked')
        if(request.form.get('symLimitToSame')): print('symLimitToSame checked')
        if(request.form.get('silentPeriod')): print('silentPeriod checked')

        for field in list(request.form):
            print(field, "=", request.form.get(field)) #.name, " ==== ", field.description, " ==== ", field.label.text, " ==== ", field.data)

            #Values
            if(field == "landscape"): d['landscape'] = request.form.get(field)
            if(field == "continuousPlayback.endTime"): d['continuousPlayback']['endTime'] = request.form.get(field)
            if(field == "continuousPlayback.ambience1"): d['continuousPlayback']['ambience1'] = request.form.get(field)
            if(field == "continuousPlayback.ambience2"): d['continuousPlayback']['ambience2'] = request.form.get(field)
            if(field == "motionTriggers.frequency"): d['motionTriggers']['frequency'] = request.form.get(field)
            
            if(field == "symphony.maximum"): d['symphony']['maximum'] = request.form.get(field)
            if(field == "silentPeriod.startTime"): d['silentPeriod']['startTime'] = request.form.get(field)
            if(field == "silentPeriod.endTime"): d['silentPeriod']['endTime'] = request.form.get(field)
            if(field == "volume"): d['volume'] = request.form.get(field)
        
        #Checkboxes
        d['continuousPlayback']['enabled'] = True if(request.form.get("continuousPlayback.enabled")) else False
        d['continuousPlayback']['upStageEnabled'] = True if(request.form.get("continuousPlayback.upStageEnabled")) else False
        d['motionTriggers']['enabled'] = True if(request.form.get("motionTriggers.enabled")) else False
        d['symphony']['enabled'] = True if(request.form.get("symphony.enabled")) else False
        d['symphony']['limitToSameType'] = True if(request.form.get("symphony.limitToSameType")) else False
        d['silentPeriod']['enabled'] = True if(request.form.get("silentPeriod.enabled")) else False

        #Values

        #Convert to json
        jsonStr = json.dumps(d)
        print("jsonStr type: ",type(jsonStr))
        print(jsonStr)

        #Push to database
        updateAppSettings(jsonStr)
        print("************* END *************")

    return(settings())

@app.route("/settings.html", methods=['post', 'get'])
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

    data = fetchAppSettings()
    settings = list(data)[0]
    print("\nSettings: ",settings)
    print("Type of settings: ", type(settings))

    print(settings['settings'])
    s = settings['settings']
    lu = settings['last_updated']
    print(lu)
    print("Type of s: ", type(s))
    d = json.loads(s)
    print("Type of d: ", type(d))

    #print(settings['settings']['continuousPlayback']['enabled'])
    print(d['landscape'])
    print(d['continuousPlayback']['enabled'])
    print(d['continuousPlayback']['endTime'])
    print(d['continuousPlayback']['ambience1'])
    print(d['continuousPlayback']['ambience2'])
    print(d['motionTriggers']['enabled'])
    print(d['motionTriggers']['frequency'])
    print(d['symphony']['enabled'])
    print(d['symphony']['maximum'])
    print(d['symphony']['limitToSameType'])
    print(d['silentPeriod']['enabled'])
    print(d['silentPeriod']['startTime'])
    print(d['silentPeriod']['endTime'])
    print(d['volume'])

    #Fetch options for 'landscape'
    landscapeLocations = list(getLandscapeLocations())
    
    #Fetch options for 'ambience'

    
    settingsTemplateData = {
        'last_updated' : settings['last_updated'],
        'landscape' : d['landscape'],
        'landscapeLocations' : landscapeLocations,
        'cbEnabled' : d['continuousPlayback']['enabled'],
        'cbEndTime' : d['continuousPlayback']['endTime'],
        'ambienceEnabled' : d['continuousPlayback']['upStageEnabled'],
        'ambience1' : d['continuousPlayback']['ambience1'],
        'ambience2' : d['continuousPlayback']['ambience2'],
        'mtEnabled' : d['motionTriggers']['enabled'],
        'mtPeriod' : d['motionTriggers']['frequency'],
        'symphony' : d['symphony']['enabled'],
        'symMaxBirds' : d['symphony']['maximum'],
        'symLimitToSame' : d['symphony']['limitToSameType'],
        'silentPeriod' : d['silentPeriod']['enabled'],
        'spStartTime' : d['silentPeriod']['startTime'],
        'spEndTime' : d['silentPeriod']['endTime'],
        'volume' : d['volume']
    }
    
    templateData.update(settingsTemplateData)
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