// script pour la balle de la page log in

    const ball = document.getElementById('ball');
    let angle = 90;
    let speedX = 2;
    let speedY = 2;
    let posX = window.innerWidth / 2;
    let posY = window.innerWidth / 2;

    function updateBackground() {
        // document.body.style.background = `linear-gradient(${angle}deg, #ff006a, #00ffdd)`;
        document.body.style.background = `linear-gradient(${angle}deg, #e4712e, #1490e2)`;
    }

    function launchBall() {
        posX += speedX;
        posY += speedY;

        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;
        const ballWidth = ball.offsetWidth;
        const ballHeight = ball.offsetHeight;

        if (posX <= 0) {
            speedX *= -1;
            angle = 90;
        }

        if (posX + ballWidth >= windowWidth) {
            speedX *= -1;
            angle = 270;
        }

        if (posY <= 0) {
            speedY *= -1;
            angle = 180;
        }

        if (posY + ballHeight >= windowHeight) {
            speedY *= -1;
            angle = 0;
        }

        updateBackground(angle);
        ball.style.left = posX + 'px';
        ball.style.top = posY + 'px';

    }

    setInterval(launchBall, 3);

// script pour garder actif le choix de la langue

    const language = document.querySelectorAll('.chooseLanguage');
    language.forEach(item => {
        item.addEventListener('click', () => {
            language.forEach(item => {
                item.classList.remove('active');
            });

            item.classList.add('active');
        });
    });

// script pour fermer les messages d alerte

    function closeAlert(divMsg) {
    var alert = divMsg.parentElement;
    alert.style.animation = 'slideOut 0.5s forwards';
    alert.addEventListener('animationend', function() {
        alert.remove();
    });
    }
    const divMsg = document.getElementById('div-message');
    setTimeout(function() {
    closeAlert(divMsg);
    }, 4000);

    
    // script pour la modale du jeu Match Local
    
    document.addEventListener('DOMContentLoaded', function() {
        var pongScript;
        var canvasModal = document.getElementById('localMatchModal');
        
        canvasModal.addEventListener('submit', function(event) {
            event.preventDefault();
            document.querySelector('#formViewLocal').style.display = 'none';
            pongScript = document.createElement('script');
            pongScript.src = '../static/scripts/ponglocal.js';
            pongScript.defer = true;
            document.body.appendChild(pongScript);
            document.querySelector('#gameViewLocal').style.display = 'block';
        });
        canvasModal.addEventListener('hidden.bs.modal', function () {
            if (pongScript) {
                document.body.removeChild(pongScript);
                pongScript = null;
            }
            document.querySelector('#formViewLocal').style.display = 'block';
            document.querySelector('#gameViewLocal').style.display = 'none';
        });
    });
    
// script pour la modale du jeu Tournament Online
    
    document.addEventListener('DOMContentLoaded', function() {
        var pongScript;
        var canvasOnlineTour = document.getElementById('onlineTournament');
        
        canvasOnlineTour.addEventListener('submit', function(event) {
            startCountdown();
            event.preventDefault();
            document.querySelector('#formViewOnlineTour').style.display = 'none';
            document.querySelector('#waitViewOnlineTour').style.display = 'block';
        });
        canvasOnlineTour.addEventListener('hidden.bs.modal', function () {
            if (pongScript) {
                document.body.removeChild(pongScript);
                pongScript = null;
            }
            document.querySelector('#onlineTourForm').style.display = 'block';
            document.querySelector('#gameViewLocal').style.display = 'none';
        });
    });
    
// script pour le chrono de chargement du Tournoi Online
function startCountdown() {
    let startCount = 2;
    const	stopCount = 0,	
            duration = 2000,
            countDownElement = document.getElementById('countdown'),
            intervalTime = duration/Math.abs(startCount - stopCount);
        
    let countDown = setInterval(function(){
        if(startCount === stopCount)
            startCount = "Go!",  
            setTimeout(() => {
                document.querySelector('#waitViewOnlineTour').style.display = 'none',
                document.querySelector('#drawViewOnlineTour').style.display = 'block'
                document.querySelector('#playViewOnlineTour').style.display = 'block'
                // AJOUTER LANCEMENT DU SCRIPT ONLINE TOURNAMENT ICI
            }, 1000),
            clearInterval(countDown)
        countDownElement.innerHTML = startCount;
        if(startCount > stopCount)
            startCount--
        else
            startCount++
        },
    intervalTime
    );
}

// script pour updater les stats en temps réel

let url = `wss://${window.location.host}/ws/stats/`
var socket = new WebSocket(url);

socket.onopen = function(e) {
    console.log("Connection established stats");
};

socket.onmessage = function(e) {
    var stats = JSON.parse(e.data);
    console.log(stats);
    console.log("envoie des donnes stats");

    let userElement = document.getElementById('stats-profile-' + stats.id);
    console.log("user id recuperer par le js:", stats.id);
    if (userElement) {
        userElement.querySelector('#won').textContent = "M. won (" + stats.won + ")";
        userElement.querySelector('#lost').textContent = "M. lost (" + stats.lost + ")";
        var lost = userElement.querySelector('.progressLost');
        lost.style.width = stats.lp + '%';
        lost.setAttribute('aria-valuenow', stats.lp);
        lost.textContent = stats.lp + '%';  
        var won = userElement.querySelector('.progressWon');
        won.style.width = stats.wp + '%';
        won.setAttribute('aria-valuenow', stats.wp);
        won.textContent = stats.wp + '%';   
        userElement.querySelector('#tourn').innerHTML = "<i class='bi bi-trophy'></i> Tournament(s) won (" + stats.tourn + ")";
    }

    var popoverElement = document.getElementById('profile-' + stats.id);
    var dateJoined = popoverElement.getAttribute('data-date-joined');
    console.log("id du popover:", popoverElement);
    console.log("stats dans le popover", stats);
    var popover = bootstrap.Popover.getInstance(popoverElement); // Get existing popover instance
    if (popover) {
        popover.dispose(); // Dispose existing popover
    }
    // Create new popover with updated content
    popover = new bootstrap.Popover(popoverElement, {
        content: `<i class='bi bi-trophy-fill'></i> Won (${stats.tourn}) tournament(s)
        <br><i class='bi bi-joystick'></i> Played (${stats.won + stats.lost}) matches:
        <br>&nbsp;&nbsp;&nbsp;&nbsp;<i class='bi bi-caret-right-fill'></i>won (${stats.won})
        <br>&nbsp;&nbsp;&nbsp;&nbsp;<i class='bi bi-caret-right-fill'></i>lost (${stats.lost})
        <br><i class='bi bi-calendar-check-fill'></i> Joined on ${dateJoined}`,
        html:true
    });
};

socket.onclose = function(e) {
    console.log("Connection closed stats");
};

socket.onerror = function(e) {
    console.log("Error occurred stats");
};


// script pour reinitialiser les forms des modales apres fermeture

document.addEventListener('DOMContentLoaded', function() {
    var signUpModal = document.getElementById('signupModal');
    var updateProfileModal = document.getElementById('profileModal');
    var localMatchModal = document.getElementById('localMatchModal')

    signUpModal.addEventListener('hidden.bs.modal', function (e) {
        document.getElementById('signupForm').reset();
    });
    updateProfileModal.addEventListener('hidden.bs.modal', function (e) {
        document.getElementById('updateProfileForm').reset();
    });
    localMatchModal.addEventListener('hidden.bs.modal', function (e) {
        document.getElementById('localMatchForm').reset();
    });
});


// script pour lancer les popovers

document.addEventListener("DOMContentLoaded", function(){
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(element){
        return new bootstrap.Popover(element, {
            html: true
        });
    });
});

