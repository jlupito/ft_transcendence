WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

WIDTH = 600
HEIGHT = 600

let delay = 30

let paddle_speed = 5

let paddle_width = 10
let paddle_height = 100

let p1_x_pos = 10
let p1_y_pos = HEIGHT / 2 - paddle_height / 2


let p2_x_pos = WIDTH - paddle_width - 10
let p2_y_pos = HEIGHT / 2 - paddle_height / 2

let p1_score = 0
let p2_score = 0

let p1_up = false
let p1_down = false
let p2_up = false
let p2_down = false

let ball_x_pos = WIDTH / 2
let ball_y_pos = HEIGHT / 2
let ball_width = 8
let ball_x_velocity = -1
let ball_y_velocity = 0
let ball_x_normalspeed = 1

const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

document.addEventListener('keydown', function(event) {
    const key = event.key;

    switch(key) {
        case 'z':
            p1_up = true;
            break;
        case 's':
            p1_down = true;
            break;
        case 'ArrowUp':
            p2_up = true;
            break;
        case 'ArrowDown':
            p2_down = true;
            break;
    }
});

document.addEventListener('keyup', function(event) {
    const key = event.key;

    switch(key) {
        case 'z':
            p1_up = false;
            break;
        case 's':
            p1_down = false;
            break;
        case 'ArrowUp':
            p2_up = false;
            break;
        case 'ArrowDown':
            p2_down = false;
            break;
    }
});

// Dessiner un rectangle rouge



function draw_objects(){
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'white';
    ctx.fillRect(p1_x_pos,  p1_y_pos, paddle_width, paddle_height);
    ctx.fillRect(p2_x_pos,  p2_y_pos, paddle_width, paddle_height);
    ctx.beginPath();
    ctx.arc(ball_x_pos, ball_y_pos, ball_width, 0, Math.PI * 2);
    ctx.fill();
    ctx.closePath();
    ctx.font = "45px sans-serif"
    ctx.fillText(p2_score, WIDTH / 4, HEIGHT / 4, 45)
    ctx.fillText(p1_score, WIDTH * 3 / 4, HEIGHT / 4, 45)
}

function apply_player_movement(){
    if (p1_up)
        p1_y_pos = Math.max(p1_y_pos - paddle_speed, 0)
    else if (p1_down)
        p1_y_pos = Math.min(p1_y_pos + paddle_speed, HEIGHT - paddle_height)
    if (p2_up)
        p2_y_pos = Math.max(p2_y_pos - paddle_speed, 0)
    else if (p2_down)
        p2_y_pos = Math.min(p2_y_pos + paddle_speed, HEIGHT - paddle_height)
}
function apply_ball_movement(){
    if (ball_x_pos + ball_x_velocity < p1_x_pos + paddle_width
        && (p1_y_pos < ball_y_pos + ball_y_velocity + ball_width && ball_y_pos + ball_y_velocity + ball_width < p1_y_pos + paddle_height + 10)){
        ball_x_velocity = -(ball_x_velocity - 0.1)
        ball_y_velocity = (p1_y_pos + paddle_height / 2 - ball_y_pos) / 16
        ball_y_velocity = -ball_y_velocity
    }
    else if (ball_x_pos + ball_x_velocity < 0){
        p1_score = p1_score + 1
        ball_x_pos = WIDTH / 2
        ball_y_pos = HEIGHT / 2
        ball_x_velocity = 1
        ball_y_velocity = 0
        p1_y_pos = HEIGHT / 2 - paddle_height / 2
        p2_y_pos = HEIGHT / 2 - paddle_height / 2
    }
    if ((ball_x_pos + ball_x_velocity > p2_x_pos - paddle_width)
        && (p2_y_pos < ball_y_pos + ball_y_velocity + ball_width && ball_y_pos + ball_y_velocity + ball_width < p2_y_pos + paddle_height + 10)){
        ball_x_velocity = -(ball_x_velocity + 0.1)
        ball_y_velocity = (p2_y_pos + paddle_height / 2 - ball_y_pos) / 16
        ball_y_velocity = -ball_y_velocity
    }
    else if (ball_x_pos + ball_x_velocity > HEIGHT){
        p2_score = p2_score + 1
        ball_x_pos = WIDTH / 2
        ball_y_pos = HEIGHT / 2
        ball_x_velocity = -1
        ball_y_velocity = 0
        p1_y_pos = HEIGHT / 2 - paddle_height / 2
        p2_y_pos = HEIGHT / 2 - paddle_height / 2
    }
    if (ball_y_pos + ball_y_velocity > HEIGHT || ball_y_pos + ball_y_velocity < 0)
        ball_y_velocity = -ball_y_velocity
    
    ball_x_pos += ball_x_velocity
    ball_y_pos += ball_y_velocity
}

function draw(){
    apply_player_movement()
    apply_ball_movement()
    draw_objects()
    requestAnimationFrame(draw);
}


draw();