// FONCTION POUR LA BALLE ET LE FOND D'ECRAN LOGIN PAGE

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

// FONCTION POUR LE CHOIX DES LANGUES
const language = document.querySelectorAll('.chooseLanguage');
language.forEach(item => {
    item.addEventListener('click', () => {
        language.forEach(item => {
            item.classList.remove('active');
        });

        item.classList.add('active');
    });
});

// FONCTION POUR INIT LES POPOVERS
document.addEventListener("DOMContentLoaded", function(){
  var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
  var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl, {
      customClass: 'custom-popover'
    })
  })
});

// ************************ FONCTION DE GESTION DES MODALES *****************************

document.addEventListener('DOMContentLoaded', function() {
  var pongScript;

  document.querySelector('#localMatchForm').addEventListener('submit', function(event) {
    event.preventDefault();
    document.querySelector('#formView').style.display = 'none';
    pongScript = document.createElement('script');
    pongScript.src = '../static/scripts/ponglocal.js';
    pongScript.defer = true;
    document.body.appendChild(pongScript);
    document.querySelector('#gameView').style.display = 'block';
    // this.reset()
  });

  var canvasModal = document.getElementById('localMatchModal');
  canvasModal.addEventListener('hidden.bs.modal', function () {
    if (pongScript) {
      document.body.removeChild(pongScript);
      pongScript = null;
    }

    document.querySelector('#formView').style.display = 'block';
    document.querySelector('#gameView').style.display = 'none';
  });
});
// document.addEventListener('DOMContentLoaded', function() {
//   function setupLocalMatchModal() {
//     document.querySelector('#localMatchForm').addEventListener('submit', function(event) {
//       event.preventDefault();
//       startLocalGame();
//       });
//       function startLocalGame() {

//       document.querySelector('#form-view').style.display = 'none';
//       document.querySelector('#game-view').style.display = 'block';
//       var pongScript = document.createElement('script');
//       pongScript.src = '../static/scripts/ponglocal.js'; // Chemin vers pong.js
//       pongScript.defer = true;
//       document.body.appendChild(pongScript);
//       }
//   }
//   setupLocalMatchModal();

//   function setupMatchModal() {
//     //   waitingMessage(); // Afficher le message d'attente au début avant que les deux joueurs soient en Mode Match
//       // Mettre ici logique pour vérifier si les joueurs sont prêts à commencer le jeu
//       startGame() //pour lancer le jeu

//     //   setTimeout(startGame, 6000); // a supprimer une fois le declanchement des connexions faites
//   }

//   function waitingMessage() { // on fait un rappel du html pour le message d'attente
//       const modalBody = document.querySelector('#onlineMatchModal .modal-body');
//       modalBody.innerHTML = '<p class="my-auto me-2">Waiting for an opponent</p>' +
//                              '<div class="dot"></div>' +
//                              '<div class="dot"></div>' +
//                              '<div class="dot"></div>';
//   }

//   function startGame() {
//       const modalBody = document.querySelector('#onlineMatchModal .modal-body');
//       modalBody.innerHTML = '<div class="canvas" width="600" height="600"><canvas id="CanvasOnline" width="600" height="600"></canvas></div>';
//   }

//   setupMatchModal();
// });
