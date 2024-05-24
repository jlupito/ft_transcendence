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

// script modal et chargement du jeu local

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

// script pour le chronometre

var width = 400,
height = 400,
timePassed = 0,
timeLimit = 30;

var fields = [{
value: timeLimit,
size: timeLimit,
update: function() {
return timePassed = timePassed + 1;
}
}];

var nilArc = d3.svg.arc()
.innerRadius(width / 3 - 133)
.outerRadius(width / 3 - 133)
.startAngle(0)
.endAngle(2 * Math.PI);

var arc = d3.svg.arc()
.innerRadius(width / 3 - 55)
.outerRadius(width / 3 - 25)
.startAngle(0)
.endAngle(function(d) {
return ((d.value / d.size) * 2 * Math.PI);
});

var svg = d3.select(".countdown").append("svg")
.attr("width", width)
.attr("height", height);

var field = svg.selectAll(".field")
.data(fields)
.enter().append("g")
.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
.attr("class", "field");

var back = field.append("path")
.attr("class", "path path--background")
.attr("d", arc);

var path = field.append("path")
.attr("class", "path path--foreground");

var label = field.append("text")
.attr("class", "label")
.attr("dy", ".35em");

(function update() {

field
.each(function(d) {
  d.previous = d.value, d.value = d.update(timePassed);
});

path.transition()
.ease("elastic")
.duration(500)
.attrTween("d", arcTween);

if ((timeLimit - timePassed) <= 10)
pulseText();
else
label
.text(function(d) {
  return d.size - d.value;
});

if (timePassed <= timeLimit)
setTimeout(update, 1000 - (timePassed % 1000));
else
destroyTimer();

})();

function pulseText() {
back.classed("pulse", true);
label.classed("pulse", true);

if ((timeLimit - timePassed) >= 0) {
label.style("font-size", "120px")
  .attr("transform", "translate(0," + +4 + ")")
  .text(function(d) {
    return d.size - d.value;
  });
}

label.transition()
.ease("elastic")
.duration(900)
.style("font-size", "90px")
.attr("transform", "translate(0," + -10 + ")");
}

function destroyTimer() {
label.transition()
.ease("back")
.duration(700)
.style("opacity", "0")
.style("font-size", "5")
.attr("transform", "translate(0," + -40 + ")")
.each("end", function() {
  field.selectAll("text").remove()
});

path.transition()
.ease("back")
.duration(700)
.attr("d", nilArc);

back.transition()
.ease("back")
.duration(700)
.attr("d", nilArc)
.each("end", function() {
  field.selectAll("path").remove()
});
}

function arcTween(b) {
var i = d3.interpolate({
value: b.previous
}, b);
return function(t) {
return arc(i(t));
};
}

