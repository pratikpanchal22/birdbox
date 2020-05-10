//Globals
stageElements = [];
stageIsHidden = true;

$(document).ready(function () {
    if (!jQuery) {
        // jQuery is not loaded
        alert("Error jQuery is not loaded");
        return;
    }

    initializations();
    getOnStageMetadata();
});

function initializations() {
    stageElements = [];
    stageIsHidden = true;

    //Set left-top icon
    $('#header-left').removeClass();
    $('#header-left').addClass("fa fa-cog");

    //click handlers
    $("#header-left").click(function () {
        //settingsClickHandler();
        window.location.href = 'settings.html';
    });

    $("#idDivStage").on("click", ".childDiv", function () {
        stageChildDiv = $(this).attr("id");
        console.log("###*** childDiv clicked: " + stageChildDiv);
        id = Number(stageChildDiv.substring(10, stageChildDiv.length));

        window.location.href = 'infoPage.html?id=' + id;
    })

    $("#idSoloOnDemandButton").click(function () {
        $("#idSoloOnDemandIcon").css("color", "red");
        $.getJSON("onDemand.json?type=solo&t=" + Math.floor(Date.now() / 1000), function (result) {
            //process result ihere
            console.log(result)
        }).done(function () {
            // Scroll up
            window.scrollTo({ top: 0, behavior: 'smooth' });
            // Set message 
            // TODO: check for status before setting this message
            $('#idStageSoundState').text("Waiting for arrival of a bird");
            //change color of button back to blue
            $("#idSoloOnDemandIcon").css("color", "rgb(79, 17, 212)");
        });
    })

    $("#idSymphonyOnDemandButton").click(function () {
        $("#idSymphonyOnDemandIcon").css("color", "red");
        $.getJSON("onDemand.json?type=symphony&t=" + Math.floor(Date.now() / 1000), function (result) {
            //process result ihere
            console.log(result)
        }).done(function () {
            // Scroll up
            window.scrollTo({ top: 0, behavior: 'smooth' });
            // Set message 
            // TODO: check for status before setting this message
            $('#idStageSoundState').text("Waiting for arrival of birds");
            //change color of button back to blue
            $("#idSymphonyOnDemandIcon").css("color", "rgb(17, 62, 212)");
        });
    })
    return;
}

lostConnectionHandle = null

function getOnStageMetadata() {

    lostConnectionHandle = setTimeout(function () {
        $("#header-right").html("❌");
    }, 4000);

    $.getJSON("onStage.json?t=" + Math.floor(Date.now() / 1000), function (result) {
        processStage(result);
    }).done(function () {
        setTimeout('getOnStageMetadata()', 2000);
        // Cancel existing 
        if (lostConnectionHandle != null) {
            clearTimeout(lostConnectionHandle);
            lostConnectionHandle = null;
        }
    });
}

function lostConnection() {

}

function isSameAsStageElements(obj) {
    if (stageElements.length != obj.length) {
        return false
    }

    for (var i = 0; i < obj.length; i++) {
        if (!stageElements.includes(obj[i])) {
            return false;
        }
    }

    return true;
}

function processStage(jsonObj) {
    //console.log("received data: " +jsonObj);
    //Indicator
    updateStatusIndicator()

    localTs = Math.floor(Date.now() / 1000);
    remoteTs = parseInt(jsonObj["ts"]);
    diff = localTs - remoteTs;

    console.log("Local: " + Math.floor(Date.now() / 1000)
        + "  Remote: " + jsonObj["ts"]
        + "  Difference: " + diff);

    if (diff > 1) {
        console.log("Data too old. Skipping");
        return;
    }

    if (jsonObj["state"] == "successful") {
        console.log(jsonObj["data"])
        obj = JSON.parse(jsonObj["data"]);
        console.log("Number of entries: " + Object.keys(obj).length)

        if (isSameAsStageElements(obj)) {
            console.log("Stage is in sync with " + obj);
        }
        else {
            console.log(">>> Updating stage " + obj);
            stageElements = obj;
            searchIds = "?id="
            for (var i = 0; i < stageElements.length; i++) {
                searchIds += stageElements[i] + ",";
            }
            searchIds = searchIds.substring(0, searchIds.length - 1);
            console.log(searchIds);

            searchUrl = "idData.json" + searchIds + "&t=" + Math.floor(Date.now() / 1000);

            //Get information on all ids
            $.getJSON(searchUrl, function (result) {
                updateStage(result);
            }).done(function () {

            });

        }
    }
    else if (jsonObj["state"] == "empty") {
        console.log("Nothing active right now")
        collapseStage();
        //change: 'you are listening to' to 'you heard'
        //document.getElementById('idStageSoundState').innerHTML = "You were listening to";
        $('#idStageSoundState').text("No birds active right now. Tap the button below to call one.");
    }
    else {
        console.log("Error: State: " + jsonObj["state"])
        //hide stage
    }
}

function updateStatusIndicator1() {

    var current = $("#header-right").html();
    var newVal = "&#128993;";

    //console.log("Div.text: " + current);

    if (current == "🟢") {
        newVal = "&#128993;";
    }
    else {
        newVal = "&#128994;"
    }
    //console.log("New val: " + newVal);
    $("#header-right").html(newVal);
}

function updateStatusIndicator() {

    var current = $("#header-right").html();
    var newVal = "&#128038;";

    //console.log("Div.text: " + current);

    if (current == "🐦") {
        newVal = "🦃";
    }
    else if (current == "🦃") {
        newVal = "🦅";
    }
    else if (current == "🦅") {
        newVal = "🦆";
    }
    else if (current == "🦆") {
        newVal = "🦉";
    }
    else if (current == "🦉") {
        newVal = "🦚";
    }
    else if (current == "🦚") {
        newVal = "🦜";
    }
    else if (current == "🦜") {
        newVal = "🕊️"
    }
    else if (current == "🕊️") {
        newVal = "🦩"
    }
    else if (current == "🦩️") {
        newVal = "🦢"
    }
    else {
        newVal = "🐦";
    }
    //console.log("New val: " + newVal);
    $("#header-right").html(newVal);
}

function updateStage(data) {
    //console.log(data);

    if (data["state"] != "successful") {
        console.log("data.state != successful.")
        return;
    }

    obj = JSON.parse(data["data"]);
    console.log("Size of data: " + obj.length);
    //console.log("Data: " + JSON.stringify(obj));

    //SoundState
    if (obj.length > 1) {
        $('#idStageSoundState').text("You are listening to a " + obj.length + "-bird symphony");
    }
    else {
        $('#idStageSoundState').text("You are listening to a");
    }


    //Remove all current childDivs
    //$("#idDivStage").empty();
    //Remove child divs that no longer exist in stageElements
    $("#idDivStage").children().each(function () {
        stageChildDiv = $(this).attr("id");

        if (stageChildDiv === undefined) {

        }
        else {
            id = Number(stageChildDiv.substring(10, stageChildDiv.length));

            if (!stageElements.includes(id)) {
                //remove
                console.log("Removing: " + stageChildDiv);

                if ($('#' + stageChildDiv).css('opacity') == 0) {
                    //remove immediately
                    console.log("******** Removing " + stageChildDiv + " immediately")
                    $(this).remove();
                }

                $('#' + stageChildDiv).css('opacity', 1)
                    .slideUp(1000)
                    .animate(
                        { opacity: 0 },
                        { queue: false, duration: 1000 }
                    );
            }
        }
    });

    if (stageIsHidden) {
        stageIsHidden = false;
        //Enable stage
        //document.getElementById("idDivStage").style.display = "block";
        //$(document.getElementById("idDivStage")).fadeIn(4000)
        $("#idDivStage").css('opacity', 0);
        $("#idDivStage").slideDown(1);
        $("#idDivStage").animate(
            { opacity: 1 },
            { queue: false, duration: 1 }
        );
    }

    //Add all new ones
    for (var i = 0; i < obj.length; i++) {

        //console.log("stringify obj: " + JSON.stringify(obj[i]));
        var o = obj[i];
        //console.log("stringify o: " + JSON.stringify(o));

        //if element is already on the list, skip
        if ($('#idChildDiv' + String(o.id)).length) {
            console.log("Child div " + o.id + " exists! Skipping");
            continue;
        }

        console.log("\nAdding child div for idx:" + o.id);

        var divId = "idChildDiv" + String(o.id);
        var nameId = "idChildName" + String(o.id);
        var imageId = "idChildImage" + String(o.id);
        childDiv = '<div id="' + divId + '" class="childDiv" style="display: none;"><center>' +
            '<h3 id="' + nameId + '">' + o.name + '</h3>' +
            '<img id="' + imageId + '" src="static/images/' + o.image_file + '" alt="Stage Image" width="100%" height="auto">' +
            '<i>(tap for more)</i>' +
            '<br/><br/>'
        '</center></div>';

        /*$("#idDivStage").append(childDiv).animate(
            {opacity: 1},
            {queue: false, duration: 1000}
        );*/
        //$(childDiv).appendTo($('#idDivStage')).slideDown(1000);
        $(childDiv).prependTo($('#idDivStage')).slideDown(1000);
    }

    /*if(stageIsHidden){
        stageIsHidden = false;
        //Enable stage
        //document.getElementById("idDivStage").style.display = "block";
        //$(document.getElementById("idDivStage")).fadeIn(4000)
        $("#idDivStage").css('opacity', 0);
        $("#idDivStage").slideDown(2500);
        $("#idDivStage").animate(
                {opacity: 1},
                {queue: false, duration: 2500}
            );
    }*/
    return;
}

function collapseStage() {
    //document.getElementById("idDivStage").style.display = "none";
    //$(document.getElementById("idDivStage")).fadeOut(4000)
    $("#idDivStage").css('opacity', 1)
        .slideUp(2000)
        .animate(
            { opacity: 0 },
            { queue: false, duration: 2000 }
        );

    stageIsHidden = true;
}