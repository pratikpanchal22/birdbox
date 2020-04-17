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
    }
    else {
        console.log("Error: State: " + jsonObj["state"])
        //hide stage
    }
 }

 function updateStage(jsonObj){

    //Name 
    document.getElementById('idStageName').innerHTML = jsonObj["name"];

    //Image
    document.getElementById('idStageImage').src = 'static/images/stageImage.JPG?t='+Math.random();
    
    //Enable stage
    document.getElementById("idDivStage").style.display = "block";
 }

 function collapseStage(){
    document.getElementById("idDivStage").style.display = "none";
 }