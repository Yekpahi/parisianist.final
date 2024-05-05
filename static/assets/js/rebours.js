// static/countdown.js
document.addEventListener('DOMContentLoaded', function() {
    var launchDate = new Date('{{ countdown.launch_date }}');
    var countdownElement = document.getElementById('countdown');

    function updateCountdown() {
        var now = new Date();
        var timeRemaining = launchDate - now;

        var days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
        var hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);

        countdownElement.innerHTML = days + "d " + hours + "h "
        + minutes + "m " + seconds + "s ";

        if (timeRemaining < 0) {
            clearInterval(interval);
            countdownElement.innerHTML = "Lancement du site !";
        }
    }

    updateCountdown();
    var interval = setInterval(updateCountdown, 1000);
});