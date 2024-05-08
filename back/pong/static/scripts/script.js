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

// gestion de la modale pour lancer le local game
// Empêcher le comportement par défaut du formulaire
document.addEventListener('DOMContentLoaded', function() {
  document.querySelector('#localMatchForm').addEventListener('submit', function(event) {
      event.preventDefault();

    });
});
