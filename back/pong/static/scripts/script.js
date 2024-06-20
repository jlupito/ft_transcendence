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

// script pour updater les stats en temps réel dans le dashboard 
//+ les popovers 
//+ les modales match history

let url = `wss://${window.location.host}/ws/stats/`
var socket = new WebSocket(url);

socket.onopen = function(e) {
console.log("Connection established stats");
};

socket.onmessage = function(e) {
    var stats = JSON.parse(e.data);
    // console.log(stats);
    // console.log("envoie des donnes stats");

    var statsElement = document.getElementById('stats-profile-' + stats.id);
    console.log("coucou", stats)
    console.log("user id recuperer par le js:", stats.id);
    if (statsElement) {
        statsElement.querySelector('#won').textContent = "(" + stats.won + ")";
        statsElement.querySelector('#lost').textContent = "(" + stats.lost + ")";
        var lost = statsElement.querySelector('.progressLost');
        lost.style.width = stats.lp + '%';
        lost.setAttribute('aria-valuenow', stats.lp);
        lost.textContent = stats.lp + '%';  
        var won = statsElement.querySelector('.progressWon');
        won.style.width = stats.wp + '%';
        won.setAttribute('aria-valuenow', stats.wp);
        won.textContent = stats.wp + '%';   
        statsElement.querySelector('#tourn').innerHTML = "<i class='bi bi-trophy-fill me-1'></i> Tournament(s) won (" + stats.tourn + ")";
        console.log(stats)
    }

    var lastMatch = stats.matches[stats.matches.length - 1]; 
    var lossesList = document.getElementById('losses-history-' + stats.id);
    if (lossesList) {
        if (lastMatch.result === 'Loss') {
            lossesList.innerHTML = '';
            for (let match of stats.matches) {
                // let match = stats.matches[index];
                if (match.result === 'Loss') {
                    var lossesElement = document.createElement('li');
                    lossesElement.innerHTML = `
                    <p class="mb-1">
                    <span class="bg-danger p-1 rounded-1 text-light shadow-sm px-2">loss</span>
                    vs <span class="bg-white bg-opacity-50 p-1 rounded-1 text-dark shadow-sm px-2">${match.opponent_name}</span>
                    (${match.user_score} - ${match.opponent_score})
                    </p>
                    <p class="ms-3 fw-light text-dark text-opacity-75">played on ${match.time}</p>
                    `;
                    lossesList.appendChild(lossesElement);
                }
            }
        }
    }
    var winsList = document.getElementById('wins-history-' + stats.id);
    if (winsList) {
        if (lastMatch.result === 'Win') {
            for (let match of stats.matches) {
                // let match = stats.matches[index];
                if (match.result === 'Win') {
                    var winsElement = document.createElement('li');
                    winsElement.innerHTML = `
                    <p class="mb-1">
                    <span class="bg-primary p-1 rounded-1 text-light shadow-sm px-2">win</span>
                    vs <span class="bg-white bg-opacity-50 p-1 rounded-1 text-dark shadow-sm px-2">${match.opponent_name}</span>
                    (${match.user_score} - ${match.opponent_score})
                    </p>
                    <p class="ms-3 fw-light text-dark text-opacity-75">played on ${match.time}</p>
                    `;
                    winsList.appendChild(winsElement);
                }
            }
        }
    }

    var popoverElement = document.getElementById('profile-' + stats.id);
    var dateJoined = popoverElement.getAttribute('data-date-joined');
    var popover = bootstrap.Popover.getInstance(popoverElement);
    if (popover) {
        popover.dispose();
    }
    popover = new bootstrap.Popover(popoverElement, {
        content: `<i class='bi bi-trophy-fill'></i> Won (${stats.tourn}) tournament(s)
        <br><i class='bi bi-joystick'></i> Played (${stats.won + stats.lost}) games:
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

// script pour les traductions


document.addEventListener('DOMContentLoaded', function() {
    var translations = {
        "english": {
            "welcome": "Welcome",
            "edit": "Edit profile",
            "update": "Update profile",
            "username": "Username",
            "picture": "Profile picture",
            "save": "Save",
            "close": "Close",
            "language": "Language",
            "authors": "Authors",
            "game": "Game",
            "play": "Play a:",
            "tournament": "Tournament",
            "won": "Games won",
            "lost": "Games lost",
            "tourn": "Tournament(s) won",
            "1v1": "Play a 1v1 match:",
            "online": "Online",
        },
        "français": {
            "welcome": "Bienvenue",
            "edit": "Modifier profil",
            "update": "Mise à jour du profil",
            "username": "Nom d'utilisateur",
            "picture": "Photo de profil",
            "save": "Enregistrer",
            "close": "Fermer",
            "language": "Langue",
            "authors": "Auteurs",
            "game": "Jeu",
            "play": "Démarrer un :",
            "tournament": "Tournoi",
            "won": "Victoires",
            "lost": "Défaites",
            "tourn": "Tournoi(s) gagné(s)",
            "1v1": "Jouer un match 1v1 :",
            "online": "En ligne",
        },
        "español": {
            "welcome": "Bienvenid@",
            "edit": "Editar perfil",
            "update": "Actualización del perfil",
            "username": "Nombre de usuari@",
            "picture": "Foto de perfil",
            "save": "Guardar",
            "close": "Cerrar",
            "language": "Idioma",
            "authors": "Autores",
            "game": "Juego",
            "play": "Iniciar un :",
            "tournament": "Torneo",
            "won": "Exitos",
            "lost": "Derrotas",
            "tourn": "Torneo(s) ganado(s)",
            "1v1": "Jugar un partido 1v1 :",
            "online": "En línea",
        }
    };
    
    var buttons = document.querySelectorAll('.chooseLanguage');
    buttons.forEach(function(button) {
        button.addEventListener('click', function() {
            var language = this.textContent.trim().toLowerCase();
            var elements = document.querySelectorAll('[data-translate]');
            elements.forEach(function(element) {
                var translation = translations[language][element.getAttribute('data-translate')];
                if (translation) {
                    element.textContent = translation;
                }
            });
        });
    });
});