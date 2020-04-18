//Globals
stageJsonObj = {};

$(document).ready(function(){
    if (!jQuery) {  
      // jQuery is not loaded
      alert("Error jQuery is not loaded");
      return;
    }

    initializations();
    getOnStageMetadata();
 });

 function initializations(){
     stageJsonObj = {"id":-1};
     return;
 }

 function getOnStageMetadata(){
     $.getJSON("onStage.json?t="+Date.now(), function(result){
         processStage(result);
     }).done(function(){
         setTimeout('getOnStageMetadata()', 2000);
     });
 }
 
 function processStage(jsonObj){
    //console.log(jsonObj);
    //jsonObj = JSON.parse(result);
    if(jsonObj["state"] == "successful"){
        if(stageJsonObj["id"] != jsonObj["id"]){
            stageJsonObj["id"] = jsonObj["id"]
            console.log("Updating stage with new id="+stageJsonObj["id"])
            updateStage(jsonObj)
        }
        else {
            console.log("Stage is in sync with id="+stageJsonObj["id"])
        }
    }
    else if(jsonObj["state"] == "empty"){
        console.log("Nothing active right now")
        collapseStage();
        //change: 'you are listening to' to 'you heard'
        //document.getElementById('idStageSoundState').innerHTML = "You were listening to";
        $('#idStageSoundState').text("You were listening to");
    }
    else {
        console.log("Error: State: " + jsonObj["state"])
        //hide stage
    }
 }

 function updateStage(jsonObj){

    //SoundState
    //document.getElementById('idStageSoundState').innerHTML = "You are listening to";
    $('#idStageSoundState').text("You are listening to");

    //Name 
    document.getElementById('idStageName').innerHTML = jsonObj["name"];

    //Image
    document.getElementById('idStageImage').src = 'static/images/'+ jsonObj["image_file"] +'?t='+Math.random();

    //Image description
    document.getElementById('idStageImageDesc').innerHTML = jsonObj["image_desc"];

    //Audio - description
    document.getElementById('idStageAudioDesc').innerHTML = jsonObj["description"];

    //Audio - type
    document.getElementById('idStageAudioType').innerHTML = "&#9838; Type: "+ jsonObj["audio_type"];

    //Audio - Location
    document.getElementById('idStageLocation').innerHTML = "&#127966; "+ jsonObj["location"];

    //Duration
    document.getElementById('idStageDuration').innerHTML = "&#9202; "+ jsonObj["duration"] + " seconds";

    //Credits
    document.getElementById('idStageCredits').innerHTML = jsonObj["date_created_or_captured"] + ", " + jsonObj["credit"];

    //Audio
    var audio = $("#idAudio");
    var sourceUrl = 'static/sounds/'+jsonObj["audio_file"]+'?t='+Math.random();
    $("#idAudioSrcMp3").attr("src", sourceUrl);
    audio[0].pause(); //pause
    audio[0].currentTime = 0; //reset time
    audio[0].load(); // reload source


    
    //Enable stage
    //document.getElementById("idDivStage").style.display = "block";
    $(document.getElementById("idDivStage")).fadeIn(4000)
 }

 function collapseStage(){
    //document.getElementById("idDivStage").style.display = "none";
    $(document.getElementById("idDivStage")).fadeOut(4000)
 }