from flask import Flask, render_template, jsonify, request
from flask_mysqldb import MySQL
import os
from threading import Thread
import datetime
import time
import json
from json import JSONEncoder
import ast
from enum import Enum
from dateutil.tz import tzlocal
import math
from decimal import Decimal
#
from common.utility import logger
from common.audio_interface import AlsaVolume as av
from common.utility import DateTimeEncoder as dte
from models import dbConfig as dbc
from models.data import Models
from models.data import ModelType
from interface import interface as interface
from interface.app_settings import AppSettings


apl = Flask(__name__)

apl.config['MYSQL_USER'] = dbc.MYSQL_USER
apl.config['MYSQL_PASSWORD'] = dbc.MYSQL_PASSWORD
apl.config['MYSQL_HOST'] = dbc.MYSQL_HOST
apl.config['MYSQL_DB'] = dbc.MYSQL_DB
apl.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(apl)

#################### App Routes ########################
@apl.route("/")
@apl.route("/index.htm")
@apl.route("/index.html")
def index():
    ts = str(int(time.time()))

    jsInclude = '<script src="/static/js/scripts.js?t='+ts+'"></script>'
    jsInclude += '<script src="https://kit.fontawesome.com/7daabcbab0.js" crossorigin="anonymous"></script>'
    
    cssInclude = '<link rel="stylesheet" href="static/css/styles.css?t='+ts+'">'
    
    templateData = {
        'jsInclude' : jsInclude,
        'cssInclude' : cssInclude
    }
    return render_template('index.html', **templateData)

@apl.route("/infoPage.html")
def infoPage():    
    #Grab the id from url parameters
    id = request.args.get("id")
    #Fetch model
    data = Models(mysql.connection).fetch(ModelType.INFO_FOR_ID, id)

    #If the data returned is not exactly 1, go to home page
    if(len(data) != 1):
        return index()

    ts = str(int(time.time()))

    jsInclude = '<script src="/static/js/scripts.js?t='+ts+'"></script>'
    jsInclude += '<script src="/static/js/infoPageScripts.js?t='+ts+'"></script>'
    jsInclude += '<script src="https://kit.fontawesome.com/7daabcbab0.js" crossorigin="anonymous"></script>'
    cssInclude = '<link rel="stylesheet" href="static/css/styles.css?t='+ts+'">'

    templateData = {
        'jsInclude' : jsInclude,
        'cssInclude' : cssInclude
    }

    templateData.update(data[0])

    #Pass to template Data
    return render_template('infoPage.html', **templateData)

@apl.route("/saveSettings.json", methods=['post', 'get'])
def saveSettings():

    logger("_INFO_", "Entering@:", str(int(time.time())))

    ts = str(int(time.time()))
    response = {
        "state":"unsuccessful",
        "ts": ts,
        "last_updated": ""
    }

    #Get current copy of settings
    a = AppSettings()
    #logger("_INFO_", "Current settings id=", a.getId())
    d = a.getSettings()

    if(request.method == 'POST'):
        #logger("_INFO_", "\n*********** form data ******************")
        #logger("_INFO_", "request.form: ", request.form)

        #if(request.form.get('cbSwitch')): print('cbSwitch checked')
        #if(request.form.get('upstageSwitch')): print('upstageSwitch checked')
        #if(request.form.get('mtEnabled')): print('mtEnabled checked')
        #if(request.form.get('symphonySwitch')): print('symphonySwitch checked')
        #if(request.form.get('symLimitToSame')): print('symLimitToSame checked')
        #if(request.form.get('silentPeriod')): print('silentPeriod checked')

        for field in list(request.form):
            #print(field, "=", request.form.get(field)) #.name, " ==== ", field.description, " ==== ", field.label.text, " ==== ", field.data)
            #logger("_INFO_", " >>> ", field, "=", request.form.get(field))

            #Values
            if(field == "landscape"): d['landscape'] = request.form.get(field)
            
            elif(field == "continuousPlayback.ambience1"): d['continuousPlayback']['ambience1'] = request.form.get(field)
            elif(field == "continuousPlayback.amb1Vol"): d['continuousPlayback']['amb1Vol'] = request.form.get(field)
            elif(field == "continuousPlayback.ambience2"): d['continuousPlayback']['ambience2'] = request.form.get(field)
            elif(field == "continuousPlayback.amb2Vol"): d['continuousPlayback']['amb2Vol'] = request.form.get(field)
            elif(field == "continuousPlayback.endTime"): d['continuousPlayback']['endTime'] = request.form.get(field)

            elif(field == "motionTriggers.frequency"): d['motionTriggers']['frequency'] = request.form.get(field)
            
            elif(field == "symphony.maximum"): d['symphony']['maximum'] = request.form.get(field)

            elif(field == "silentPeriod.startTime"): d['silentPeriod']['startTime'] = request.form.get(field)
            elif(field == "silentPeriod.endTime"): d['silentPeriod']['endTime'] = request.form.get(field)
            
            elif(field == "volume"): d['volume'] = request.form.get(field)
            
            elif(field == "continuousPlayback.enabled" or 
                 field == "continuousPlayback.birds" or
                 field == "continuousPlayback.upStageEnabled" or
                 field == "motionTriggers.enabled" or
                 field == "symphony.enabled" or
                 field == "symphony.limitToSameType" or
                 field == "silentPeriod.enabled"): 
                    #logger("_INFO_", "Checkbox", field, "handled outside loop")
                    continue

            else: logger("_INFO_", "ERROR! Form field/value: ", field,"/",request.form.get(field)," NOT BEING HANDLED")
        
        #Checkboxes
        d['continuousPlayback']['enabled'] = True if(request.form.get("continuousPlayback.enabled")) else False
        d['continuousPlayback']['birdsEnabled'] = True if(request.form.get("continuousPlayback.birds")) else False
        d['continuousPlayback']['upStageEnabled'] = True if(request.form.get("continuousPlayback.upStageEnabled")) else False

        d['motionTriggers']['enabled'] = True if(request.form.get("motionTriggers.enabled")) else False

        d['symphony']['enabled'] = True if(request.form.get("symphony.enabled")) else False
        d['symphony']['limitToSameType'] = True if(request.form.get("symphony.limitToSameType")) else False

        d['silentPeriod']['enabled'] = True if(request.form.get("silentPeriod.enabled")) else False

        #Convert to json
        jsonStr = json.dumps(d)
        #logger("_INFO_", "Json settings string to be saved: ", jsonStr)

        #Push to database
        a.save(jsonStr)
        #logger("_INFO_", "\nSettings saved. New id=",a.getId())
        #logger("_INFO_", "************* END *************")

        #Invoke settingsChange handler
        ambientSoundscapeThread = Thread(target=interface.settingsChangeHandler(), args=[1, 4])
        ambientSoundscapeThread.name = "ambientSoundScapeThread"
        ambientSoundscapeThread.start()

        #Set state of response
        response['state'] = 'successful'

    #logger("_INFO_", "Last updated: ", a.getLastUpdated(), " time-zone:", datetime.datetime.now(tzlocal()).tzname())
    response['last_updated'] = str(a.getLastUpdated()) + " " + datetime.datetime.now(tzlocal()).tzname()
    logger("_INFO_", "Exiting@:", str(int(time.time())))
    return(jsonify(response))

@apl.route("/settings.html", methods=['post', 'get'])
def settings():
    ts = str(int(time.time()))

    jsInclude = '<script src="/static/js/scripts.js?t='+ts+'"></script>'
    jsInclude += '<script src="/static/js/settings.js?t='+ts+'"></script>'
    jsInclude += '<script src="https://kit.fontawesome.com/7daabcbab0.js" crossorigin="anonymous"></script>'
    cssInclude = '<link rel="stylesheet" href="static/css/styles.css?t='+ts+'">'
    cssInclude += '<link rel="stylesheet" href="static/css/settings.css?t='+ts+'">'

    templateData = {
        'jsInclude' : jsInclude,
        'cssInclude' : cssInclude
    }

    a = AppSettings()
    d = a.getSettings()
    #print("Type of d: ", type(d))

    #print(settings['settings']['continuousPlayback']['enabled'])
    #print(d['landscape'])
    #print(d['continuousPlayback']['enabled'])
    #print(d['continuousPlayback']['endTime'])
    #print(d['continuousPlayback']['ambience1'])
    #print(d['continuousPlayback']['ambience2'])
    #print(d['motionTriggers']['enabled'])
    #print(d['motionTriggers']['frequency'])
    #print(d['symphony']['enabled'])
    #print(d['symphony']['maximum'])
    #print(d['symphony']['limitToSameType'])
    #print(d['silentPeriod']['enabled'])
    #print(d['silentPeriod']['startTime'])
    #print(d['silentPeriod']['endTime'])
    #print(d['volume'])

    #Fetch options for 'landscape'
    landscapeLocations = Models(mysql.connection).fetch(ModelType.LIST_OF_LOCATIONS)
    
    #Fetch options for 'ambience'
    soundscapes = Models(mysql.connection).fetch(ModelType.LIST_OF_SOUNDSCAPES_FOR_LOC, d['landscape'])
    
    #Insert an empty item as an option for user to select
    emptyItem = {'name' : 'None'}
    soundscapes.insert(0, emptyItem)

    #Prepopulate endTime if continuousPlayback is disabled
    if(d['continuousPlayback']['enabled'] == False):
        defaultEndTime = datetime.datetime.now() + datetime.timedelta(minutes = 30) 
        d['continuousPlayback']['endTime'] = defaultEndTime.strftime("%H:%M")

    settingsTemplateData = {
        'last_updated' : a.getLastUpdated(),
        
        'landscape' : d['landscape'],
        'landscapeLocations' : landscapeLocations,

        'cbEnabled' : d['continuousPlayback']['enabled'],
        'birdsEnabled' : d['continuousPlayback']['birdsEnabled'],
        'ambienceEnabled' : d['continuousPlayback']['upStageEnabled'],
        'ambience1' : d['continuousPlayback']['ambience1'],
        'amb1Vol' : d['continuousPlayback']['amb1Vol'],
        'ambience2' : d['continuousPlayback']['ambience2'],
        'amb2Vol' : d['continuousPlayback']['amb2Vol'],
        'cbEndTime' : d['continuousPlayback']['endTime'],
        'ambientLocations' : soundscapes,
        
        'mtEnabled' : d['motionTriggers']['enabled'],
        'mtPeriod' : d['motionTriggers']['frequency'],
        'symphony' : d['symphony']['enabled'],
        'symMaxBirds' : d['symphony']['maximum'],
        'symLimitToSame' : d['symphony']['limitToSameType'],
        'silentPeriod' : d['silentPeriod']['enabled'],
        'spStartTime' : d['silentPeriod']['startTime'],
        'spEndTime' : d['silentPeriod']['endTime'],
        #'volume' : d['volume']
        'volume' : av.getCurrentVolume()
    }
    
    templateData.update(settingsTemplateData)
    return render_template('settings.html', **templateData)    

@apl.route("/onDemand.json", methods=['get'])
def onDemand():
    ts = str(int(time.time()))

    onDemandType = request.args.get("type")

    response = {
        "state":"unsuccessful",
        "ts": ts
    }

    triggerType = interface.TriggerType.UNSUPPORTED_TRIGGER
    if(onDemandType == "solo"):
        triggerType = interface.TriggerType.ON_DEMAND_SOLO
    elif(onDemandType == "symphony"):
        triggerType = interface.TriggerType.ON_DEMAND_SYMPHONY
    else: 
        return jsonify(response)

    t = Thread(target=interface.processTrigger, args=[(triggerType)])
    t.name = "thread_"+onDemandType+"_"+str(ts)
    t.start()

    response['state'] = "successful"
    return jsonify(response)

@apl.route("/onStage.json")
def onStage():
    ts = str(int(time.time()))
    
    t = request.args.get("t")

    #print("local ts=",ts," t=",t," diff=",int(ts)-int(t))

    jsonObj = {
        "state":"unknown",
        "ts":ts
    }

    if(int(ts) - int(t) > 2):
        #Request too old
        jsonObj["state"] = "request too old"
        print("Rejecting request because it is too old", jsonObj)
        return jsonify(jsonObj)

    refetch = True
    while refetch==True:
        entries = None
        entries = Models(mysql.connection).fetch(ModelType.ACTIVE_ENTRIES)
        entries = [e['id'] for e in entries]
        logger("_INFO_", "\nfetchActiveEntries: ", json.dumps(entries))
        if(len(entries)==0):
            jsonObj["state"] = "empty"
            refetch = False
        else:
            purged = interface.purgeDeadEntries(60)
            print("Entries purged: ", purged)
            if(purged == 0):
                refetch = False
                jsonObj["state"] = "successful"
                jsonObj["data"] = json.dumps(entries)
            else:
                refetch = True

    return json.dumps(jsonObj)

@apl.route("/idData.json")
def idData():
    ts = str(int(time.time()))
    
    t = request.args.get("t")
    comma_separated_ids = request.args.get("id")
    #ids = u.comma_separated_params_to_list(request.args.get("id"))
    #print ("\n\n############# ids: ",ids)
    #for id in ids:
    #    print ("id: ",id)

    #print("local ts=",ts," t=",t," diff=",int(ts)-int(t))

    jsonObj = {
        "state":"unknown",
        "ts":ts
    }

    if(int(ts) - int(t) > 2):
        #Request too old
        jsonObj["state"] = "request too old"
        print("Rejecting request because it is too old", jsonObj)
        return jsonify(jsonObj)

    entries = Models(mysql.connection).fetch(ModelType.METADATA_FOR_IDS, comma_separated_ids)
    print("\nConverting entries to JSON:")
    print(json.dumps(entries, cls=dte))

    if(len(entries)==0):
        jsonObj["state"] = "empty"
    else:
        jsonObj["state"] = "successful"
        jsonObj["data"] = json.dumps(entries, cls=dte)

    return json.dumps(jsonObj)

@apl.route("/getCombinatoricData.json")
def combinatoricData():
    ts = str(int(time.time()))

    response = {
        "state":"unsuccessful",
        "ts": ts
    }
    
    location = request.args.get("landscape")
    r = int(request.args.get("channels"))
    logger("_INFO_", "location=", location)

    d = Models(mysql.connection).fetch(ModelType.LOCATION_INFO, location)

    logger("_INFO_", "d=", d)
    logger("_INFO_", "d[totalBirdSounds]=", d[0]['totalBirdSounds'])
    #combinations = nCr
    n = d[0]['totalBirdSounds']
    if(n>0 and r>0):
        combInt = math.factorial(n)/(math.factorial(n-r) * math.factorial(r))
        comb = '{:.0}'.format(math.factorial(n)/(math.factorial(n-r) * math.factorial(r)))
        logger("_INFO_", "Combinations: ", comb, " Probability=", str(100/combInt))

        landscapeSubData = "This landscape has " + str(d[0]["distinctBirds"]) + " unique birds, " + str(d[0]["totalBirdSounds"]) + " songs, calls and other birdsounds, and " + str(d[0]["landscapeSounds"]) + " ambient soundscapes."
        channelsSubData = "With this setting, the number of birdsounds combinations possible are " + '{:,}'.format(combInt)[:-2] + ". Or in other words, the probability of listening to the same combination is " + f"{Decimal(100/combInt):.4E}" +"%"
        
        response["state"] = "successful"
        response["landscapeSubData"] = landscapeSubData
        response["channelsSubData"] = channelsSubData

    return json.dumps(response)

if __name__ == "__main__":
    apl.run(host='0.0.0.0', port=80, debug=True)