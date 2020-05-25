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
from models import dbConfig as dbc
from interface import interface as interface
from common.utility import DateTimeEncoder as dte

apl = Flask(__name__)

apl.config['MYSQL_USER'] = dbc.MYSQL_USER
apl.config['MYSQL_PASSWORD'] = dbc.MYSQL_PASSWORD
apl.config['MYSQL_HOST'] = dbc.MYSQL_HOST
apl.config['MYSQL_DB'] = dbc.MYSQL_DB
apl.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(apl)

#################### App Models #######################
#MODEL TYPES
class ModelType(Enum):
    UNINITIALIZED_MODEL_TYPE = 0
    #Fetch
    ACTIVE_ENTRIES = 1
    METADATA_FOR_IDS = 2
    INFO_FOR_ID = 3
    APP_SETTINGS = 4
    LIST_OF_LOCATIONS = 5
    LIST_OF_SOUNDSCAPES_FOR_LOC = 6
    LOCATION_INFO = 7
    #Push

class Models:
    def __init__(self, sql):
        self.sql = sql
        self.modelType = ModelType.UNINITIALIZED_MODEL_TYPE
        self.query = ""
        
    def fetch(self, modelType, *argv):
        self.modelType = modelType
        
        if(self.modelType == ModelType.ACTIVE_ENTRIES):
            self.query = "SELECT "+dbc.KEY_ID+" FROM birdboxTable WHERE ("+dbc.KEY_ACTIVE+" = true AND "+dbc.KEY_AUDIO_TYPE+" != '"+dbc.KEY_AUDIO_TYPE_VAL_SOUNDSCAPE+"');"
        elif(self.modelType == ModelType.APP_SETTINGS):
            self.query = "SELECT "+dbc.KEY_ID+", "+dbc.KEY_LAST_UPDATED+", "+dbc.KEY_SETTINGS+" "+" FROM "+dbc.TABLE_SETTINGS+" ORDER BY "+dbc.KEY_ID+" DESC LIMIT 1;"
        elif(self.modelType == ModelType.LIST_OF_LOCATIONS):
            self.query = "SELECT DISTINCT "+dbc.KEY_LOCATION+" from birdboxTable;"
        elif(self.modelType == ModelType.LIST_OF_SOUNDSCAPES_FOR_LOC):
            try:
                loc = argv[0]
            except:
                print("ERROR: Expected location")
                return
            self.query = "SELECT "+dbc.KEY_NAME+" from birdboxTable WHERE ("+dbc.KEY_AUDIO_TYPE+" = '"+dbc.KEY_AUDIO_TYPE_VAL_SOUNDSCAPE+"' AND "+dbc.KEY_LOCATION+" = '"+loc+"');"
        elif(self.modelType == ModelType.METADATA_FOR_IDS):
            try:
                comma_separated_ids = argv[0]
            except:
                print("ERROR: Expected comma_sep_values")
                return
            comma_separated_ids = argv[0]
            self.query = "SELECT "+dbc.KEY_ID+", "+dbc.KEY_NAME+", "+dbc.KEY_IMAGE_FILE+" "+" FROM birdboxTable where "+dbc.KEY_ID+" in (" + comma_separated_ids + ");"
        elif(self.modelType == ModelType.INFO_FOR_ID):
            try:
                id = argv[0]
            except:
                print("ERROR: Expected id")
                return
            self.query = "SELECT "+dbc.KEY_ID+", "+dbc.KEY_NAME+", "+dbc.KEY_AUDIO_FILE+", "+dbc.KEY_AUDIO_TYPE+", "+dbc.KEY_DESCRIPTION+", "+dbc.KEY_DURATION+", "+dbc.KEY_CREDIT+", "+dbc.KEY_DATE_CREATED_OR_CAPTURED+", "+dbc.KEY_IMAGE_FILE+", "+dbc.KEY_IMAGE_DESC+", "+dbc.KEY_LOCATION+", "+dbc.KEY_URL+" "+" FROM birdboxTable where "+dbc.KEY_ID+" = " + str(id)+";"
        elif(self.modelType == ModelType.LOCATION_INFO):
            try:
                loc = argv[0]
            except:
                print("Error: Expected location")
                return
            self.query = ("SELECT COUNT(*) as total, "
                            + "(SELECT COUNT(distinct name) FROM birdboxTable WHERE audio_type != 'soundscape' and location = '"+str(loc)+"') as distinctBirds, "
                            + "(SELECT COUNT(distinct audio_file) FROM birdboxTable WHERE audio_type != 'soundscape' and location = '"+str(loc)+"') as totalBirdSounds, "
                            + "(SELECT COUNT(distinct audio_file) FROM birdboxTable WHERE audio_type = 'soundscape' and location = '"+str(loc)+"') as landscapeSounds "
                         +"FROM birdboxTable WHERE location = '"+str(loc)+"';")
        else:
            print("ERROR: Unsupported model type: ",str(self.modelType))
            return
        
        if(self.query == ""):
            print("Error! Empty query / unsupported ModelType")
            return
        
        #logger("_INFO_", "Query: ", self.query)
        cursor = self.sql.connection.cursor()
        cursor.execute(self.query)
        r = list(cursor.fetchall())
        cursor.close()
        #self.sql.connection.close()
        return r

    def push(self, modelType, *argv):
        self.modelType = modelType

        if(self.modelType == ModelType.APP_SETTINGS):
            try:
                s = argv[0]
            except:
                print("ERROR: Expected string of settings")
                return
            self.query = "INSERT INTO "+dbc.TABLE_SETTINGS+" ("+dbc.KEY_SETTINGS+") VALUES ('" + s + "');"

        if(self.query == ""):
            print("Error! Empty query / unsupported ModelType")
            return

        conn=self.sql.connection
        cursor = conn.cursor()
        results = cursor.execute(self.query)
        conn.commit()
        cursor.close()
        return results

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
    data = Models(mysql).fetch(ModelType.INFO_FOR_ID, id)

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

    ts = str(int(time.time()))
    response = {
        "state":"unsuccessful",
        "ts": ts,
        "last_updated": ""
    }

    #Get current copy of settings
    a = Models(mysql).fetch(ModelType.APP_SETTINGS)
    d = json.loads(a[0]['settings'])

    if(request.method == 'POST'):
        print("\n\n *********** form data ******************")
        print("request.data: ", request.data)
        print("request.form: ", request.form)
        
        #if(request.form.get('cbSwitch')): print('cbSwitch checked')
        #if(request.form.get('upstageSwitch')): print('upstageSwitch checked')
        #if(request.form.get('mtEnabled')): print('mtEnabled checked')
        #if(request.form.get('symphonySwitch')): print('symphonySwitch checked')
        #if(request.form.get('symLimitToSame')): print('symLimitToSame checked')
        #if(request.form.get('silentPeriod')): print('silentPeriod checked')

        for field in list(request.form):
            print(field, "=", request.form.get(field)) #.name, " ==== ", field.description, " ==== ", field.label.text, " ==== ", field.data)

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
                 field == "silentPeriod.enabled"): logger("_INFO_", "Checkbox", field, "handled outside loop")

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
        print("jsonStr type: ",type(jsonStr))
        print(jsonStr)

        #Push to database
        m = Models(mysql).push(ModelType.APP_SETTINGS, jsonStr)
        print("Settings saved. m=",m)
        print("************* END *************")

        #Refetch from database
        a = Models(mysql).fetch(ModelType.APP_SETTINGS)

        #Invoke settingsChange handler
        ambientSoundscapeThread = Thread(target=interface.settingsChangeHandler(), args=[1, 4])
        ambientSoundscapeThread.name = "ambientSoundScapeThread"
        ambientSoundscapeThread.start()

        #Set state of response
        response['state'] = 'successful'

    print("Last updated: ", a[0]['last_updated'], " time-zone:", datetime.datetime.now(tzlocal()).tzname())
    response['last_updated'] = str(a[0]['last_updated']) + " " + datetime.datetime.now(tzlocal()).tzname()
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

    #data = fetchAppSettings()
    a = Models(mysql).fetch(ModelType.APP_SETTINGS)
    settings = a[0]
    #print("\nSettings fetched. id=", settings['id'])
    #print("Settings: ",settings)
    #print("Type of settings: ", type(settings))

    #print(settings['settings'])
    s = settings['settings']
    #print("Type of s: ", type(s))
    d = json.loads(s)
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
    landscapeLocations = Models(mysql).fetch(ModelType.LIST_OF_LOCATIONS)
    
    #Fetch options for 'ambience'
    soundscapes = Models(mysql).fetch(ModelType.LIST_OF_SOUNDSCAPES_FOR_LOC, d['landscape'])
    emptyItem = {'name' : 'None'}
    soundscapes.insert(0, emptyItem)
    #print(soundscapes)

    #Prepopulate endTime if continuousPlayback is disabled
    if(d['continuousPlayback']['enabled'] == False):
        defaultEndTime = datetime.datetime.now() + datetime.timedelta(minutes = 30) 
        d['continuousPlayback']['endTime'] = defaultEndTime.strftime("%H:%M")

    settingsTemplateData = {
        'last_updated' : settings['last_updated'],
        
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
        entries = Models(mysql).fetch(ModelType.ACTIVE_ENTRIES)
        entries = [e['id'] for e in entries]
        print("\nfetchActiveEntries: ", json.dumps(entries))
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

    entries = Models(mysql).fetch(ModelType.METADATA_FOR_IDS, comma_separated_ids)
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

    d = Models(mysql).fetch(ModelType.LOCATION_INFO, location)

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