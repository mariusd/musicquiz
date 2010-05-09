/* Source: http://code.google.com/apis/youtube/js_api_reference.html */
var PlayerState = {
    UNSTARTED : -1,
    ENDED : 0,
    PLAYING : 1,
    PAUSED : 2,
    BUFFERING : 3,
    VIDEO_CUED : 5
};


/* default size "425", "356" */
var params = { allowScriptAccess: "always" };
var atts = { id: "myytplayer" };
swfobject.embedSWF(
    "http://www.youtube.com/v/" + youtube_code 
        + "?enablejsapi=1&playerapiid=ytplayer", 
    "ytapiplayer", "0", "0", "8", null, null, params, atts
);

     
function onYouTubePlayerReady(playerId) {
    ytplayer = document.getElementById("myytplayer");
    ytplayer.addEventListener("onStateChange", "onytplayerStateChange");
    ytplayer.setVolume(100);
    var position = Math.floor(Math.random() * (youtube_duration - 20 + 1));
    ytplayer.seekTo(position, true);
}

function onytplayerStateChange(newState) {
    if (formSubmitted)
        return;
    if (newState == PlayerState.PLAYING && !timerStarted) {
        timerStarted = true;
        var timerDiv = document.getElementById("timer");
        var loader = timerDiv.getElementsByTagName("img")[0];
        timerDiv.removeChild(loader);
        runTimer();
    }
}

var timeLeft = 20 * 1000;
var timerStarted = false;
var timer = null;
var formSubmitted = false;

function runTimer() {
    var timerDiv = document.getElementById("timer");
    timeLeft -= 100;
    timeLeftFloat = sprintf("%.1f", timeLeft / 1000);
    timerDiv.firstChild.nodeValue = timeLeftFloat
    var timeField = document.getElementsByName("remaining_time")[0];
    timeField.value = timeLeftFloat
    if (timeLeft < 10 * 1000) {
        timerDiv.style.color = '#CC0000';
    }
    if (timeLeft >= 100) {
        timer = setTimeout("runTimer()", 100);
    } else {
        timeOver();
    }
}

function submitForm() {
    if (formSubmitted)
        return;
    formSubmitted = true;
    if (timer != null) {
        clearTimeout(timer);
    }
    if (typeof(myVar) !== 'undefined')
        ytplayer.stopVideo();
    var form = document.getElementById("answer_form");
    form.submit();
}

function timeOver() {
    ytplayer.stopVideo();
    var form = document.getElementById("answer_form");
    form.submit();
}

//setTimeout("$('result').fade('out')", 2000);