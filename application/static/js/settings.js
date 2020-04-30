
$(document).ready(function () {
    if (!jQuery) {
        // jQuery is not loaded
        alert("Error jQuery is not loaded");
        return;
    }

    initializations();

});

function initializations() {
    //click handlers
    $("#idCbSwitch").change(function () {
        if (document.getElementById("idCbSwitch").checked == true) {
            showSubContent(idDivSubContentCb);
        }
        else {
            hideSubContent(idDivSubContentCb);
        }
    });

    if (document.getElementById("idCbSwitch").checked == true) {
        showSubContent(idDivSubContentCb);
    }
    else {
        hideSubContent(idDivSubContentCb);
    }

    $("#idUpstageSwitch").change(function () {
        if (document.getElementById("idUpstageSwitch").checked == true) {
            showSubContent(idDivSubContentUpstage);
        }
        else {
            hideSubContent(idDivSubContentUpstage);
        }
    });

    if (document.getElementById("idUpstageSwitch").checked == true) {
        showSubContent(idDivSubContentUpstage);
    }
    else {
        hideSubContent(idDivSubContentUpstage);
    }

    $("#idMotionSwitch").change(function () {
        if (document.getElementById("idMotionSwitch").checked == true) {
            showSubContent(idDivSubContentMotion);
        }
        else {
            hideSubContent(idDivSubContentMotion);
        }
    });

    if (document.getElementById("idMotionSwitch").checked == true) {
        showSubContent(idDivSubContentMotion);
    }
    else {
        hideSubContent(idDivSubContentMotion);
    }

    $("#idSymphonySwitch").change(function () {
        if (document.getElementById("idSymphonySwitch").checked == true) {
            showSubContent(idDivSubContentSymphony);
        }
        else {
            hideSubContent(idDivSubContentSymphony);
        }
    });

    if (document.getElementById("idSymphonySwitch").checked == true) {
        showSubContent(idDivSubContentSymphony);
    }
    else {
        hideSubContent(idDivSubContentSymphony);
    }

    $("#idSilentPeriodSwitch").change(function () {
        if (document.getElementById("idSilentPeriodSwitch").checked == true) {
            showSubContent(idDivSubContentSilentPeriod);
        }
        else {
            hideSubContent(idDivSubContentSilentPeriod);
        }
    });

    if (document.getElementById("idSilentPeriodSwitch").checked == true) {
        showSubContent(idDivSubContentSilentPeriod);
    }
    else {
        hideSubContent(idDivSubContentSilentPeriod);
    }

    /*$("#idVolumeSlider").on('change',function () {
        $("#idVolVal").text($("#idVolumeSlider").val() + "%");
    });*/

    var slide = document.getElementById('idVolumeSlider');
    var VolVal = document.getElementById('idVolVal');
    slide.oninput = function () {
        VolVal.innerHTML = this.value + "%";
    }
   


    //Fetch this settings from Server
    //document.getElementById("idSilentPeriodSwitch").checked = true;

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