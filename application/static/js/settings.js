
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

function initializations() {

    //Set left-top icon
    $('#header-left').removeClass();
    $('#header-left').addClass("fa fa-home");

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

    $("#idSilentPeriodSwitch").change(function () {
        setVisibility(idDivSubContentSilentPeriod, document.getElementById("idSilentPeriodSwitch").checked);
    });

    /*$("#idVolumeSlider").on('change',function () {
        $("#idVolVal").text($("#idVolumeSlider").val() + "%");
    });*/

    var amb1Slide = document.getElementById('idAmb1VolumeSlider');
    amb1Slide.oninput = function () {
        document.getElementById('idAmb1VolVal').innerHTML = this.value + "%";
        flagToPushSettings();
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
    document.getElementById("idForm").action = "saveSettings.json?t="+Math.floor(Date.now()/1000);

    return;
}

function flagToPushSettings(){
    console.log("flag to push settings");
    glPushSettingsOnNextIteration = true;

    if(glReadyForNextPush){
        pushSettings();
    }
}

function pushSettings(){
    console.log("Push settings");
    if(glPushSettingsOnNextIteration == false){
        return;
    }

    glPushSettingsOnNextIteration = false;
    glReadyForNextPush = false;

    $.post("saveSettingsLive.json?t="+ Math.floor(Date.now() / 1000), 
                $('#idForm').serialize(), function(data, textStatus){
                    console.log("Response status: " + textStatus);
                    console.log("Received response: " + data);
                    setTimeout(function(){
                        glReadyForNextPush = true;
                        pushSettings();
                    }, 1000);
                });
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