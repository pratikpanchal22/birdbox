//Globals
stageElements = [];
settingsViewEnabled = false;
stageIsHidden = true;

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
    stageElements = [];
    stageIsHidden = true;

     //click handlers
     $("#header-left").click(function(){
        settingsClickHandler();
     });
     
     $("#idDivStage").on("click", ".childDiv", function(){
         console.log("###*** childDiv clicked: " + $(this).attr("id"));
     })
     return;
 }

 function getOnStageMetadata(){
     $.getJSON("onStage.json?t="+Math.floor(Date.now()/1000), function(result){
         processStage(result);
     }).done(function(){
         setTimeout('getOnStageMetadata()', 2000);
     });
 }

 function isSameAsStageElements(obj){
    if(stageElements.length != obj.length){
        return false
    }

    for(var i=0; i<obj.length; i++){
        if(!stageElements.includes(obj[i])){
            return false;
        }
    }

    return true;
 }
 
 function processStage(jsonObj){
    //console.log("received data: " +jsonObj);
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
        console.log(jsonObj["data"])
        obj = JSON.parse(jsonObj["data"]);
        console.log("Number of entries: " + Object.keys(obj).length)

        if(isSameAsStageElements(obj)){
            console.log("Stage is in sync with " + obj);
        }
        else {
            console.log(">>> Updating stage " + obj);
            stageElements = obj;
            searchIds = "?id="
            for(var i=0; i<stageElements.length; i++){
                searchIds += stageElements[i] + ",";
            }
            searchIds = searchIds.substring(0, searchIds.length-1);
            console.log(searchIds);

            searchUrl = "idData.json" + searchIds + "&t=" + Math.floor(Date.now()/1000);

            //Get information on all ids
            $.getJSON(searchUrl, function(result){
                updateStage(result);       
            }).done(function(){
                
            });
                    
        }
    }
    else if(jsonObj["state"] == "empty"){
        console.log("Nothing active right now")
        collapseStage();
        //change: 'you are listening to' to 'you heard'
        //document.getElementById('idStageSoundState').innerHTML = "You were listening to";
        $('#idStageSoundState').text("No birds active right now");
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

 function updateStage(data){
    //console.log(data);

    if(data["state"] != "successful"){
        console.log("data.state != successful.")
        return;
    }

    obj = JSON.parse(data["data"]); 
    console.log("Size of data: " + obj.length);
    //console.log("Data: " + JSON.stringify(obj));
    
    //SoundState
    if(obj.length > 1){
        $('#idStageSoundState').text("You are listening to a "+obj.length+"-bird symphony");
    }
    else {
        $('#idStageSoundState').text("You are listening to a");
    }


    //Remove all current childDivs
    //$("#idDivStage").empty();
    //Remove child divs that no longer exist in stageElements
    $("#idDivStage").children().each(function(){
        stageChildDiv = $(this).attr("id");

        if(stageChildDiv === undefined){
            
        }
        else {
            id = Number(stageChildDiv.substring(10, stageChildDiv.length));

            if(!stageElements.includes(id)){
                //remove
                console.log("Removing: " + stageChildDiv);

                if($('#'+stageChildDiv).css('opacity') == 0){
                    //remove immediately
                    console.log("******** Removing " + stageChildDiv + " immediately")
                    $(this).remove();
                }

                $('#'+stageChildDiv).css('opacity', 1)
                    .slideUp(1000)
                    .animate(
                        {opacity: 0},
                        {queue: false, duration: 1000}
                    );                
            }
        }
    });

    //Add all new ones
    for(var i=0; i<obj.length; i++){

        //console.log("stringify obj: " + JSON.stringify(obj[i]));
        var o = obj[i];
        //console.log("stringify o: " + JSON.stringify(o));

        //if element is already on the list, skip
        if($('#idChildDiv'+String(o.id)).length){
            console.log("Child div " + o.id + " exists! Skipping");
            continue;
        }

        console.log("\nAdding child div for idx:" + o.id);

        var divId = "idChildDiv" + String(o.id);
        var nameId = "idChildName" + String(o.id);
        var imageId = "idChildImage" + String(o.id);
        childDiv = '<div id="'+divId+'" class="childDiv" style="display: none;"><center>'+
                    '<h3 id="'+nameId+'">'+o.name+'</h3>'+ 
                    '<img id="'+imageId+'" src="static/images/'+o.image_file+'" alt="Stage Image" width="100%" height="auto">'+
                    '<br/><br/>'
                    '</center></div>';

        /*$("#idDivStage").append(childDiv).animate(
            {opacity: 1},
            {queue: false, duration: 1000}
        );*/
        $(childDiv).appendTo($('#idDivStage')).slideDown(1000);
    }

    if(stageIsHidden){
        stageIsHidden = false;
        //Enable stage
        //document.getElementById("idDivStage").style.display = "block";
        //$(document.getElementById("idDivStage")).fadeIn(4000)
        $("#idDivStage").css('opacity', 0);
        $("#idDivStage").slideDown(1000);
        $("#idDivStage").animate(
                {opacity: 1},
                {queue: false, duration: 1000}
            );
    }
    return;
    

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

    //Do not enable stage if in settings 
    if(settingsViewEnabled){
        return;
    }
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
    
    stageIsHidden = true;
 }

 function settingsClickHandler(){
    console.log("settings clicked");
    if(settingsViewEnabled){
        settingsViewEnabled = false;
        $("#idDivStageStatus").css(
            'display','block',
            'overflow','hidden'
        );
        $("#idMainName").css(
            'display','block',
            'overflow','hidden'
        );
        $("#idDivSettings").css(
            'display','none',
            'overflow','hidden'
        );
        //remove class - remvoe animation
        //$(".fa").removeClass("fa-spin");
    }
    else {
        settingsViewEnabled = true;
        $("#idDivStage").css(
            'display','none',
            'overflow','hidden'
        );
        $("#idDivStageStatus").css(
            'display','none',
            'overflow','hidden'
        );
        $("#idMainName").css(
            'display','none',
            'overflow','hidden'
        );
        $("#idDivSettings").css(
            'display','block',
            'overflow','hidden'
        );
        //Add class - add animation
        //$(".fa").addClass("fa-spin");
        //$("#header-left").css('transform', 'none');
    }
 }