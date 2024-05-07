import json
from channels.generic.websocket import WebsocketConsumer
import channels.layers
from asgiref.sync import async_to_sync
from django.core.cache import cache
from channels.generic.websocket import WebsocketConsumer
import threading
import time


games = []

class Game():
    def __init__(self, maxscore):
        self.delay = 30
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.player1 = ""
        self.player2 = ""

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
        self.maxscore = maxscore

        self.p1_up = False
        self.p1_down = False
        self.p2_up = False
        self.p2_down = False

        self.ball_x_pos = self.WIDTH / 2
        self.ball_y_pos = self.HEIGHT / 2
        self.ball_width = 8
        self.ball_x_velocity = 10
        self.ball_y_velocity = 0
        self.ball_x_normalspeed = 10
        self.has_finished = False

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
            self.ball_x_velocity = self.ball_x_normalspeed
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
            self.ball_x_velocity = -self.ball_x_normalspeed
            self.ball_y_velocity = 0
            self.p1_y_pos = self.HEIGHT / 2 -self.paddle_height / 2
            self.p2_y_pos = self.HEIGHT / 2 -self.paddle_height / 2
        if (self.ball_y_pos + self.ball_y_velocity > self.HEIGHT or self.ball_y_pos + self.ball_y_velocity < 0):
            self.ball_y_velocity = -self.ball_y_velocity

        self.ball_x_pos += self.ball_x_velocity
        self.ball_y_pos += self.ball_y_velocity

        if (self.p1_score >= self.maxscore or self.p2_score >= self.maxscore):
            self.endgame()

    def run(self):
        self.is_running = True
        while self.is_running:
            self.apply_player_movement()
            self.apply_ball_movement()
            time.sleep(0.025)

    def start(self):
        thread = threading.Thread(target=self.run)
        thread.start()

    def endgame(self):
        self.is_running = False #Stop la loop du jeu et sortira du thread
        self.has_finished = True


        


# def get_user_count():
#     return cache.get('users_count', 0)

# class MyConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Ajoutez l'utilisateur au groupe de canaux
#         await self.channel_layer.group_add("users", self.channel_name)

#         # Incrémentez le compteur dans le cache
#         cache.add('users_count', 0)
#         cache.incr('users_count')
        

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Retirez l'utilisateur du groupe de canaux
#         await self.channel_layer.group_discard("users", self.channel_name)

#         # Décrémentez le compteur dans le cache
#         cache.decr('users_count')




class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = None

    def connect(self):
        # self.room_group_name = 'test'

        # async_to_sync(self.channel_layer.group_add)(
        #     self.room_group_name,
        #     self.channel_name
        # )
        self.accept()
        # if (games):
        #     newgames = []
        #     gamelist = None
        #     for gamelist in games:
        #         if (gamelist.has_finished == False):
        #             newgames.append(gamelist)
        #     games = newgames
        user = self.scope['user']
        for game in games:
            if (game.has_finished == False and (game.player1 == user.username or game.player2 == user.username)):
                self.game = game
                break
            if (self.game == None and game.has_finished == False and (game.player1 == "" or game.player2 == "")):
                self.game = game
                if (self.game.player1 == "" and self.game.player2 != user.username):
                    self.game.player1 = user.username
                elif (self.game.player2 == "" and self.game.player1 != user.username):
                    self.game.player2 = user.username
                break
        
        if (self.game == None):
            self.game = Game(5)
            self.game.player1 = user.username
            games.append(self.game)
        if (self.game.player1 != "" and self.game.player2 != ""):
            self.game.start()
        self.send(text_data=json.dumps({
            'type':'connection_established',
            'message':'you are connected',
            'data':(self.game.__dict__)
        }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username
        if (message == 'update'):
            self.send_update()
        if (message == 'key_up_pressed' and self.game.player1 == username):
            self.game.p1_up = True
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p1 up'
            }))
        if (message == 'key_up_released' and self.game.player1 == username):
            self.game.p1_up = False
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p1 up released'
            }))
        if (message == 'key_down_pressed' and self.game.player1 == username):
            self.game.p1_down = True
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p1 down'
            }))
        if (message == 'key_down_released' and self.game.player1 == username):
            self.game.p1_down = False
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p1 down released'
            }))
        if (message == 'p2key_up_pressed' and self.game.player2 == username):
            self.game.p2_up = True
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p2 up pressed'
            }))
        if (message == 'p2key_up_released' and self.game.player2 == username):
            self.game.p2_up = False
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p2 up released'
            }))
        if (message == 'p2key_down_pressed' and self.game.player2 == username):
            self.game.p2_down = True
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p2 down pressed'
            }))
        if (message == 'p2key_down_released' and self.game.player2 == username):
            self.game.p2_down = False
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p2 down released'
            }))
        # if (message == 'replay'):
        #     user = self.scope['user']
        #     game = None
        #     for game in games:
        #         if (game.player1 == user.username or game.player2 == user.username):
        #             break
        #         if (self.game == None and (game.player1 == "" or game.player2 == "")):
        #             self.game = game
        #         if (self.game.player1 == "" and self.game.player2 != user.username):
        #             self.game.player1 = user.username
        #         elif (self.game.player2 == "" and self.game.player1 != user.username):
        #             self.game.player2 = user.username
        #         break
        #     if (game == None and self.game == None):
        #         self.game = Game(5)
        #         self.game.player1 = user.username
        #         games.append(self.game)
        #     if (self.game.player1 != "" and self.game.player2 != ""):
        #         self.game.start()
            
    
    def send_update(self):
        self.send(text_data=json.dumps({
            'type':'update received',
            'data': self.game.__dict__
        }))
    