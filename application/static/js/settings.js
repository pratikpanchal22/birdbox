
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

    $("#idUpstageSwitch").change(function () {
        setVisibility(idDivSubContentUpstage, document.getElementById("idUpstageSwitch").checked);
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

    var slide = document.getElementById('idVolumeSlider');
    var VolVal = document.getElementById('idVolVal');
    slide.oninput = function () {
        VolVal.innerHTML = this.value + "%";
    }
   
    //Set form submit action listener
    document.getElementById("idForm").action = "saveSettings.json?t="+Math.floor(Date.now()/1000);

    return;
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