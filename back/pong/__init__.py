
import threading
import time


class Game():
    def __init__(self):
        self.delay = 30
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        self.WIDTH = 600
        self.HEIGHT = 600

        self.paddle_speed = 5
        self.paddle_width = 10
        self.paddle_height = 100

        self.p1_x_pos = 10
        self.p1_y_pos = self.HEIGHT / 2 - self.paddle_height / 2


        self.p2_x_pos = self.WIDTH - self.paddle_width - 10
        self.p2_y_pos = self.HEIGHT / 2 - self.paddle_height / 2

        self.p1_score = 0
        self.p2_score = 0

        self.p1_up = False
        self.p1_down = False
        self.p2_up = False
        self.p2_down = False

        self.ball_x_pos = self.WIDTH / 2
        self.ball_y_pos = self.HEIGHT / 2
        self.ball_width = 8
        self.ball_x_velocity = 2.5
        self.ball_y_velocity = 0
        self.ball_x_normalspeed = 1

    def apply_player_movement(self):
        if (self.p1_up):
            self.p1_y_pos = max(self.p1_y_pos - self.paddle_speed, 0)
        elif (self.p1_down):
            self.p1_y_pos = min(self.p1_y_pos + self.paddle_speed, self.HEIGHT - self.paddle_height)
        if (self.p2_up):
            self.p2_y_pos = max(self.p2_y_pos - self.paddle_speed, 0)
        elif (self.p2_down):
            self.p2_y_pos = min(self.p2_y_pos + self.paddle_speed, self.HEIGHT - self.paddle_height)

    def apply_ball_movement(self):
        if (self.ball_x_pos + self.ball_x_velocity < self.p1_x_pos + self.paddle_width
            and (self.p1_y_pos < self.ball_y_pos + self.ball_y_velocity + self.ball_width and self.ball_y_pos + self.ball_y_velocity + self.ball_width < self.p1_y_pos + self.paddle_height + 10)):
            self.ball_x_velocity = -(self.ball_x_velocity - 0.1)
            self.ball_y_velocity = (self.p1_y_pos + self.paddle_height / 2 - self.ball_y_pos) / 16
            self.ball_y_velocity = -self.ball_y_velocity
        
        elif (self.ball_x_pos + self.ball_x_velocity < 0):
            self.p1_score = self.p1_score + 1
            self.ball_x_pos = self.WIDTH / 2
            self.ball_y_pos = self.HEIGHT / 2
            self.ball_x_velocity = 1
            self.ball_y_velocity = 0
            self.p1_y_pos = self.HEIGHT / 2 - self.paddle_height / 2
            self.p2_y_pos = self.HEIGHT / 2 - self.paddle_height / 2
        if ((self.ball_x_pos + self.ball_x_velocity > self.p2_x_pos - self.paddle_width)
            and (self.p2_y_pos < self.ball_y_pos + self.ball_y_velocity + self.ball_width and self.ball_y_pos + self.ball_y_velocity + self.ball_width < self.p2_y_pos + self.paddle_height + 10)):
            self.ball_x_velocity = -(self.ball_x_velocity + 0.1)
            self.ball_y_velocity = (self.p2_y_pos + self.paddle_height / 2 - self.ball_y_pos) / 16
            self.ball_y_velocity = -self.ball_y_velocity
        elif (self.ball_x_pos + self.ball_x_velocity > self.HEIGHT):
            self.p2_score = self.p2_score + 1
            self.ball_x_pos = self.WIDTH / 2
            self.ball_y_pos = self.HEIGHT / 2
            self.ball_x_velocity = -1
            self.ball_y_velocity = 0
            self.p1_y_pos = self.HEIGHT / 2 -self.paddle_height / 2
            self.p2_y_pos = self.HEIGHT / 2 -self.paddle_height / 2
        if (self.ball_y_pos + self.ball_y_velocity > self.HEIGHT or self.ball_y_pos + self.ball_y_velocity < 0):
            self.ball_y_velocity = -self.ball_y_velocity

        self.ball_x_pos += self.ball_x_velocity
        ball_y_pos += ball_y_velocity

    def run(self):
        self.is_running = True
        while True:
            self.apply_player_movement()
            self.apply_ball_movement()
            time.sleep(0.025)

    def start(self):
        thread = threading.Thread(target=self.run)
        thread.start()

game_instance = Game()
game_instance.start()