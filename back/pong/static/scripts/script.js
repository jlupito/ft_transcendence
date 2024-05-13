const ball = document.getElementById('ball');
let angle = 90;
let speedX = 2;
let speedY = 2;
let posX = window.innerWidth / 2;
let posY = window.innerWidth / 2;


function updateBackground() {
    document.body.style.background = `linear-gradient(${angle}deg, #ff006a, #00ffdd)`;
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
    // console.log(posX, posY);
    // console.log(windowWidth, windowHeight);

}

setInterval(launchBall, 3);

const language = document.querySelectorAll('.chooseLanguage');
language.forEach(item => {
    item.addEventListener('click', () => {
        language.forEach(item => {
            item.classList.remove('active');
        });

        item.classList.add('active');
    });
});

// FONCTION DE GESTION DES MODALES
// Empêcher le comportement par défaut de la modale + form avec event.preventDefault();
document.addEventListener('DOMContentLoaded', function() {
  function setupLocalMatchModal() {
      document.querySelector('#localMatchForm').addEventListener('submit', function(event) {
          event.preventDefault();
          startLocalGame();
      });
      function startLocalGame() {
        const modalBody = document.querySelector('#matchModal .modal-body');
        modalBody.innerHTML = '<div class="canvas" width="600" height="600"><canvas id="CanvasOnline" width="600" height="600"></canvas></div>';
      }
  }

  function setupMatchModal() {
    //   waitingMessage(); // Afficher le message d'attente au début avant que les deux joueurs soient en Mode Match
      // Mettre ici logique pour vérifier si les joueurs sont prêts à commencer le jeu
      startGame() //pour lancer le jeu

    //   setTimeout(startGame, 6000); // a supprimer une fois le declanchement des connexions faites
  }

  function waitingMessage() { // on fait un rappel du html pour le message d'attente
      const modalBody = document.querySelector('#matchModal .modal-body');
      modalBody.innerHTML = '<p class="my-auto me-2">Waiting for an opponent</p>' +
                             '<div class="dot"></div>' +
                             '<div class="dot"></div>' +
                             '<div class="dot"></div>';
  }

  function startGame() {
      const modalBody = document.querySelector('#matchModal .modal-body');
      modalBody.innerHTML = '<div class="canvas" width="600" height="600"><canvas id="CanvasOnline" width="600" height="600"></canvas></div>';
  }

  setupLocalMatchModal();
  setupMatchModal();
});
