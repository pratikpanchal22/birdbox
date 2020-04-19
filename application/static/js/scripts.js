//Globals
stageJsonObj = {};
settingsViewEnabled = false;

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

     //click handlers
     $("#header-left").click(function(){
        settingsClickHandler();
     });
     return;
 }

 function getOnStageMetadata(){
     $.getJSON("onStage.json?t="+Math.floor(Date.now()/1000), function(result){
         processStage(result);
     }).done(function(){
         setTimeout('getOnStageMetadata()', 2000);
     });
 }
 
 function processStage(jsonObj){
    //Indicator
    updateStatusIndicator()

    localTs = Math.floor(Date.now() / 1000);
    remoteTs = parseInt(jsonObj["ts"]);
    diff = localTs - remoteTs;
    console.log("Local: "+Math.floor(Date.now() / 1000)
        +"  Remote: "+jsonObj["ts"]
        +"  Difference: "+diff);

    if(diff > 1){
        console.log("Data too old. Skipping");
        return;
    }


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

 function updateStatusIndicator1(){
    
    var current = $("#header-right").html();
    var newVal = "&#128993;";

    //console.log("Div.text: " + current);
    
    if(current == "🟢") {
        newVal = "&#128993;";
    }
    else {
        newVal = "&#128994;"
    }
    //console.log("New val: " + newVal);
    $("#header-right").html(newVal);
 }

 function updateStatusIndicator(){
    
    var current = $("#header-right").html();
    var newVal = "&#128038;";

    //console.log("Div.text: " + current);
    
    if(current == "🐦") {
        newVal = "🦃";
    }
    else if (current == "🦃"){
        newVal = "🦅";
    }
    else if (current == "🦅"){
        newVal = "🦆";
    }
    else if (current == "🦆"){
        newVal = "🦉";
    }
    else if (current == "🦉"){
        newVal = "🦚";
    }    
    else if (current == "🦚"){
        newVal = "🦜";
    }
    else {
        newVal = "🐦";
    }
    //console.log("New val: " + newVal);
    $("#header-right").html(newVal);
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
    //$(document.getElementById("idDivStage")).fadeIn(4000)
    $("#idDivStage").css('opacity', 0);
    $("#idDivStage").slideDown(2000);
    $("#idDivStage").animate(
            {opacity: 1},
            {queue: false, duration: 2000}
        );
 }

 function collapseStage(){
    //document.getElementById("idDivStage").style.display = "none";
    //$(document.getElementById("idDivStage")).fadeOut(4000)
    $("#idDivStage").css('opacity', 1)
        .slideUp(2000)
        .animate(
            {opacity: 0},
            {queue: false, duration: 2000}
        );
 }

 function settingsClickHandler(){
    console.log("settings clicked");
 }