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

// script pour le chrono de chargement de la modale

    let startCount = 60;
    const	stopCount = 0,	
            duration = 60000,
            countDownElement = document.getElementById('countdown'),
            intervalTime = duration/Math.abs(startCount - stopCount);
            
    let countDown = setInterval(function(){
        if(startCount === stopCount)
            startCount = "Go!",
            clearInterval(countDown)
        countDownElement.innerHTML = startCount;
        if(startCount > stopCount)
            startCount--
        else
            startCount++
        },
    intervalTime
    );

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
            this.reset()
        });

        Array.from(document.getElementsByClassName("closeRefresh")).forEach(function(element) {
            element.addEventListener("click", function() {
                location.replace("/");
            });
        });
    });

// script pour la modale du jeu Tournament Online

document.addEventListener('DOMContentLoaded', function() {
    var pongScript;
    var canvasOnlineTour = document.getElementById('onlineTournament');

    canvasOnlineTour.addEventListener('submit', function(event) {
        event.preventDefault();
        document.querySelector('#formViewOnlineTour').style.display = 'none';
        // pongScript = document.createElement('script');
        // pongScript.src = '../static/scripts/pongtournamentonline.js';
        // pongScript.defer = true;
        // document.body.appendChild(pongScript);
        document.querySelector('#waitViewOnlineTour').style.display = 'block';
        });
        canvasOnlineTour.addEventListener('hidden.bs.modal', function () {
        if (pongScript) {
            document.body.removeChild(pongScript);
            pongScript = null;
        }
        document.querySelector('#onlineTourForm').style.display = 'block';
        document.querySelector('#gameViewLocal').style.display = 'none';
        this.reset()
        });

        Array.from(document.getElementsByClassName("closeRefresh")).forEach(function(element) {
            element.addEventListener("click", function() {
                location.replace("/");
            });
        });
    });

// fetch('http://localhost:8000/api/stats')
//     .then(response => {
//         // Vérifier si la requête a réussi
//         if (!response.ok) {
//             throw new Error('Network response was not ok');
//         }
//         // Convertir la réponse en JSON
//         return response.json();
//     })
//     .then(data => {
//         // Utiliser les données pour mettre à jour les éléments de votre page
//         document.querySelector('.won-stats').textContent = `won (${data.won})`;
//         document.querySelector('.wp-stats').style.width = `${data.wp}%`;
//         document.querySelector('.wp-stats').textContent = `${data.wp}%`;
//         document.querySelector('.lost-stats').textContent = `lost (${data.lost})`;
//         document.querySelector('.lp-stats').style.width = `${data.lp}%`;
//         document.querySelector('.lp-stats').textContent = `${data.lp}%`;
//     })
//     .catch(error => {
//         // Afficher une erreur si quelque chose se passe mal
//         console.error('There has been a problem with your fetch operation:', error);
//     });