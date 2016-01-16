// Screensaver

var mousetimeout;
var screensaver_active = false;
var idletime = 60;

function show_screensaver(){
    $('#screensaver').fadeIn();
    screensaver_active = true;
    screensaver_animation();
}

function stop_screensaver(){
    $('#screensaver').fadeOut();
    screensaver_active = false;
}

function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.round(Math.random() * 15)];
    }
    return color;
}

$(document).mousemove(function(){
    clearTimeout(mousetimeout);

    if (screensaver_active) {
        stop_screensaver();
    }

    mousetimeout = setTimeout(function(){
        show_screensaver();
    }, 1000 * idletime); // 5 secs
});

function screensaver_animation(){
    if (screensaver_active) {
        $('#screensaver').animate(
            {backgroundColor: getRandomColor()},
            400,
            screensaver_animation);
    }
}


function setTime(ts) {
  var date = new Date(ts);
  $('.time').text(date.toLocaleString(navigator.language, {
    hour: '2-digit',
    minute: '2-digit'
  })).attr('datetime', date.getHours() + ':' + date.getMinutes());
  $('.date').text(date.toLocaleString(navigator.language, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })).attr('datetime', date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate());
  setTimeout(function () {
    setTime(Date.now());
  }, 1000);
}

setTime(Date.now());