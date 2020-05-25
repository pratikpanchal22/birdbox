
glPushSettingsOnNextIteration = false;
glReadyForNextPush = true;

$(document).ready(function () {
    if (!jQuery) {
        // jQuery is not loaded
        alert("Error jQuery is not loaded");
        return;
    }

    initializations();

});

function setVisibility(targetDivId, visibility){
    if(visibility == true){
        showSubContent(targetDivId);
    }
    else {
        hideSubContent(targetDivId);
    }
}

busyIconTimerHandle = null;
function changeLeftIcon(val) {
    var c = "fa fa-home";
    if(val == 'busy'){
        //busyIconTimerHandle = -1;
        c = "fas fa-cloud-download-alt";
        if($('#header-left').hasClass("fa-cloud-download-alt")){
            c = "fas fa-cloud-upload-alt";
        }

        if(busyIconTimerHandle){
            clearTimeout(busyIconTimerHandle);
            busyIconTimerHandle = null;
        }
        
        busyIconTimerHandle = setTimeout(function(){
            changeLeftIcon('busy');
        }, 250);
        
        //console.log("timerID after setting = " + busyIconTimerHandle);
    }
    else if (val == 'home'){
        //cancel timer
        if(busyIconTimerHandle != null){
            clearTimeout(busyIconTimerHandle);
            busyIconTimerHandle = null;
        }
        c = "fa fa-home";
        //console.log("timerID after clearing = " + busyIconTimerHandle);
    }
    else {

    }

    $('#header-left').removeClass();
    $('#header-left').addClass(c);
}

function initializations() {

    //Set left-top icon
    changeLeftIcon('home');

    //Set initial visibility
    setVisibility(idDivSubContentCb, document.getElementById("idCbSwitch").checked);
    setVisibility(idDivSubContentUpstage, document.getElementById("idUpstageSwitch").checked);
    setVisibility(idDivSubContentMotion, document.getElementById("idMotionSwitch").checked);
    setVisibility(idDivSubContentSymphony, document.getElementById("idSymphonySwitch").checked);
    setVisibility(idDivSubContentSilentPeriod, document.getElementById("idSilentPeriodSwitch").checked);

    //click handlers
    //click handlers
    $("#header-left").click(function(){
        //settingsClickHandler();
        window.location.href='index.html';
    });
 
    $("#idLandscape").change(function () {
        getLandscapeInfo();
    });

    $("#idCbSwitch").change(function () {
        setVisibility(idDivSubContentCb, document.getElementById("idCbSwitch").checked);
    });

    $("#idBirdsSwitch").change(function () {
        setCompositeVisibilityAndStates1()
    });

    $("#idUpstageSwitch").change(function () {
        setVisibility(idDivSubContentUpstage, document.getElementById("idUpstageSwitch").checked);
        setCompositeVisibilityAndStates1()
    });

    $("#idAmbience1").on('change', function(){
        setCompositeVisibilityAndStates2();
    });

    $("#idAmbience2").on('change', function(){
        setCompositeVisibilityAndStates2();
    });

    $("#idMotionSwitch").change(function () {
        setVisibility(idDivSubContentMotion, document.getElementById("idMotionSwitch").checked);
    });

    $("#idSymphonySwitch").change(function () {
        setVisibility(idDivSubContentSymphony, document.getElementById("idSymphonySwitch").checked);
    });
    
    $("#idMaxNumberOfChannels").change(function () {
        getLandscapeInfo();
    });

    $("#idSilentPeriodSwitch").change(function () {
        setVisibility(idDivSubContentSilentPeriod, document.getElementById("idSilentPeriodSwitch").checked);
    });

    var amb1Slide = document.getElementById('idAmb1VolumeSlider');
    amb1Slide.oninput = function () {
        document.getElementById('idAmb1VolVal').innerHTML = this.value + "%";
    }

    var amb2Slide = document.getElementById('idAmb2VolumeSlider');
    amb2Slide.oninput = function () {
        document.getElementById('idAmb2VolVal').innerHTML = this.value + "%";
    }

    var slide = document.getElementById('idVolumeSlider');
    slide.oninput = function () {
        document.getElementById('idVolVal').innerHTML = this.value + "%";
    }
   
    //Set form submit action listener
    //document.getElementById("idForm").action = "saveSettings.json?t="+Math.floor(Date.now()/1000);
    //document.getElementById("idForm").addEventListener('change', function(e){
    document.getElementById("idForm").onchange = function(e){
        changeLeftIcon('busy');
    
        glPushSettingsOnNextIteration = true;
        if(glReadyForNextPush){
            pushSettings();
        }
    };

    //factory reset
    /*
    document.getElementById("idFactoryResetButton").onclick = function(){
        //window.location.href='/';
        console.log("TODO: implement factory reset");
    }*/

    //Landscape info
    getLandscapeInfo();

    return;
}

function pushSettings(){
    console.log("Push settings");
    if(glPushSettingsOnNextIteration == false){
        console.log("No new data. Exiting");
        changeLeftIcon('home');
        return;
    }

    glPushSettingsOnNextIteration = false;
    glReadyForNextPush = false;

    $.post("saveSettings.json?t="+ Math.floor(Date.now() / 1000), 
            $('#idForm').serialize(), function(data, textStatus){
                console.log("Response status: " + textStatus);
                console.log("Received response: " + JSON.stringify(data));

                if(textStatus == 'success'){
                    doThingsOnSuccessfulResponse(data);
                }
                else {
                    //do things on unsuccessful response
                }
            });
}

function getLandscapeInfo(){

    queryParms = {
        t : Math.floor(Date.now() / 1000),
        landscape : $('#idLandscape').find(":selected").text(),
        channels : $('#idMaxNumberOfChannels').val()
    }

    $.getJSON("getCombinatoricData.json", queryParms, function (result) {
        //process result ihere
        console.log(result)
        if (result["state"] == "successful") {
            $('#idLandscapeInfo').text(result["landscapeSubData"]);
            $('#idCombinationInfo').text(result["channelsSubData"]);
        }
        else {
            errorMessage = "This landscape doesn not have sufficient data";
            $('#idLandscapeInfo').text(errorMessage);
            $('#idCombinationInfo').text(errorMessage);
        }
    }).done(function () {

    });
}

function doThingsOnSuccessfulResponse(data){
    // Update timestamp
    $('#idHeaderLastUpdated').text("Updated on " + data.last_updated).fadeOut(100).fadeIn(200);

    // Set next callback
    setTimeout(function(){
        glReadyForNextPush = true;
        pushSettings();
    }, 250);
}

function setCompositeVisibilityAndStates1(){
    if(document.getElementById("idBirdsSwitch").checked == false && document.getElementById("idUpstageSwitch").checked == false){
        setVisibility(idDivSubContentCb, false);
        document.getElementById("idCbSwitch").checked = false;
    }
}

function setCompositeVisibilityAndStates2(){
    if(document.getElementById("idAmbience1").value == 'None' && document.getElementById("idAmbience2").value == 'None'){
        setVisibility(idDivSubContentUpstage, false);
        document.getElementById("idUpstageSwitch").checked = false;
    }
}

function hideSubContent(divId) {
    console.log("Hiding: " + divId);
    $(divId).css('opacity', 1)
        .slideUp(500)
        .animate(
            { opacity: 0 },
            { queue: false, duration: 500 }
        );
}

function showSubContent(divId) {
    console.log("Showing: " + divId);
    $(divId).css('opacity', 0)
        .slideDown(500)
        .animate(
            { opacity: 1 },
            { queue: false, duration: 500 }
        );
}