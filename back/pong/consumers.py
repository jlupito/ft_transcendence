import json
from channels.generic.websocket import WebsocketConsumer
import channels.layers
from asgiref.sync import async_to_sync
from django.core.cache import cache
from channels.generic.websocket import WebsocketConsumer
import threading
import time
from .models import Match


games_online = []
games_local = []
games_tournament = []

class Game():
    def __init__(self, maxscore, game_type):
        self.game_type = game_type
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
        if self.p1_up:
            self.p1_y_pos = max(self.p1_y_pos - self.paddle_speed, 0)
        elif self.p1_down:
            self.p1_y_pos = min(self.p1_y_pos + self.paddle_speed, self.HEIGHT - self.paddle_height)
        if self.p2_up:
            self.p2_y_pos = max(self.p2_y_pos - self.paddle_speed, 0)
        elif self.p2_down:
            self.p2_y_pos = min(self.p2_y_pos + self.paddle_speed, self.HEIGHT - self.paddle_height)

    def apply_ball_movement(self):
        if (self.ball_x_pos + self.ball_x_velocity < self.p1_x_pos + self.paddle_width
            and (self.p1_y_pos < self.ball_y_pos + self.ball_y_velocity + self.ball_width < self.p1_y_pos + self.paddle_height + 10)):
            self.ball_x_velocity = -(self.ball_x_velocity - 0.1)
            self.ball_y_velocity = (self.p1_y_pos + self.paddle_height / 2 - self.ball_y_pos) / 16
            self.ball_y_velocity = -self.ball_y_velocity

        elif self.ball_x_pos + self.ball_x_velocity < 0:
            self.p1_score += 1
            self.reset_ball_position()
        if (self.ball_x_pos + self.ball_x_velocity > self.p2_x_pos - self.paddle_width
            and (self.p2_y_pos < self.ball_y_pos + self.ball_y_velocity + self.ball_width < self.p2_y_pos + self.paddle_height + 10)):
            self.ball_x_velocity = -(self.ball_x_velocity + 0.1)
            self.ball_y_velocity = (self.p2_y_pos + self.paddle_height / 2 - self.ball_y_pos) / 16
            self.ball_y_velocity = -self.ball_y_velocity
        elif self.ball_x_pos + self.ball_x_velocity > self.WIDTH:
            self.p2_score += 1
            self.reset_ball_position()
        if self.ball_y_pos + self.ball_y_velocity > self.HEIGHT or self.ball_y_pos + self.ball_y_velocity < 0:
            self.ball_y_velocity = -self.ball_y_velocity

        self.ball_x_pos += self.ball_x_velocity
        self.ball_y_pos += self.ball_y_velocity

        if self.p1_score >= self.maxscore or self.p2_score >= self.maxscore:
            self.endgame()

    def reset_ball_position(self):
        self.ball_x_pos = self.WIDTH / 2
        self.ball_y_pos = self.HEIGHT / 2
        self.ball_x_velocity = self.ball_x_normalspeed
        self.ball_y_velocity = 0
        self.p1_y_pos = self.HEIGHT / 2 - self.paddle_height / 2
        self.p2_y_pos = self.HEIGHT / 2 - self.paddle_height / 2

    def run(self):
        self.is_running = True
        while self.is_running:
            self.apply_player_movement()
            self.apply_ball_movement()
            time.sleep(0.025)

    def start(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        self.send(text_data=json.dumps({
            'message': 'start'
        }))

    def endgame(self):
        self.is_running = False
        self.has_finished = True
        print("Final scores: Player 1 =", self.p1_score, ", Player 2 =", self.p2_score)
        new_match = Match.create_match_from_game(self)
        new_match.save()

    def key_up_pressed(self, username):
        if (username == self.player1):
            self.p1_up = True
        elif (username == self.player2):
            self.p2_up = True

    def key_up_released(self, username):
        if (username == self.player1):
            self.p1_up = False
        elif (username == self.player2):
            self.p2_up = False
    
    def key_down_pressed(self, username):
        if (username == self.player1):
            self.p1_down = True
        elif (username == self.player2):
            self.p2_down = True

    def key_down_released(self, username):
        if (username == self.player1):
            self.p1_down = False
        elif (username == self.player2):
            self.p2_down = False


class Player:
    def __init__(self, name):
        self.name = name
        self.player_status = 'Waiting'
        self.game:Game = None

class Tournament():
    def __init__(self):
        self.games = []
        self.players = []
        self.status = "Waiting"
        self.is_finished = False
        self.is_running = True
        self.timer = 60
        self.winner = None

    def add_player(self, username):
        if (self.status == "Waiting"):
            player
            for player in self.players:
                if (player == username):
                    break
            if (not player):
                self.players.append(Player(username))

    def run(self):
        while (self.is_running):
            if (self.status == "Waiting"):
                if (self.timer >= 0):
                    self.timer -= 1
                else:
                    self.status = "Started"
            if (self.status == "Starting"):
                self.games = None
                for player in self.players:
                    if (player.player_status == "Waiting"):
                        self.add_player_to_game(player)

                for player in self.players:
                    if (player.game.is_running == False and player.game.player1 != None and player.game.player2 != None):
                        player.game.start()
                        player.player_status = "Playing"
                    if (player.game.is_running == True):
                        player.player_status = "Playing"
                if (len(self.games) > 1):
                    self.status == "Started"
                else:
                    self.status == "Ending"
            if (self.status == "Started"):
                player:Player
                for player in self.players:
                    if (player.player_status == "Disqualified" or player.player_status == "Qualified"):
                        continue
                    if (player.player_status == "Waiting" and (player.game.player1 == None or player.game.player2 == None)):
                        player.player_status = "Qualified"
                    if (player.game.has_finished == True and player.game.player1 == player.name):
                        if (player.game.player1 <= player.game.player2):
                            player.player_status = "Disqualified"
                        else:
                            player.player_status = "Qualified"
                    elif (player.game.has_finished == True and player.game.player2 == player.name):
                        if (player.game.player2 <= player.game.player1):
                            player.player_status = "Disqualified"
                        else:
                            player.player_status = "Qualified"
                for player in self.players:
                    if (not player.player_status == "Qualified" and not player.player_status == "Disqualified"):
                        break
                if (player == None):
                    self.status = "Starting"
            if (self.status == "Ending"):
                for player in self.players:
                    if (player.player_status == "Waiting" and (player.game.player1 == None or player.game.player2 == None)):
                        player.player_status = "Winner"
                    if (player.game.has_finished == True and player.game.player1 == player.name):
                        if (player.game.player1 <= player.game.player2):
                            player.player_status = "Disqualified"
                        else:
                            player.player_status = "Winner"
                    elif (player.game.has_finished == True and player.game.player2 == player.name):
                        if (player.game.player2 <= player.game.player1):
                            player.player_status = "Disqualified"
                        else:
                            player.player_status = "Winner"
                            self.winner = player.name
            if (self.winner != None):
                self.is_running = False
                self.is_finished = True
                self.status = "Finished"
                    
                
                
    def add_player_to_game(self, player: Player):
        if (player.game == None):
            game: Game
            for game in self.games:
                if (game.player2 == None or game.player2 == player.name):
                    game.player2 = player.name
                    player.game = game
                    break
        if (game == None and player.game == None):
            new_game = Game(5, "online")
            new_game.player1 = player.name
            self.games.append(new_game)

    def start(self):
        thread = threading.Thread(target=self.run())
        thread.start()

    def getupdate(self, username):
        player:Player
        for player in self.players:
            if (player.name == username):
                return (json.dumps({
                'type': 'update received',
                'data': player.game.__dict__
            }))

    def handle_key_event(self, message, username):
        player:Player
        for player in self.players:
            if (player.name == username):
                break
        if (player == None):
            return
        if message == 'key_up_pressed':
            player.game.key_up_pressed(username)
        elif message == 'key_up_released':
            player.game.key_up_released(username)
        elif message == 'key_down_pressed':
            player.game.key_down_pressed(username)
        elif message == 'key_down_released':
            player.game.key_down_released(username)
        elif message == 'p2key_up_pressed' and player.game.game_type == "local":
            player.game.p2_up = True
        elif message == 'p2key_up_released' and player.game.game_type == "local":
            player.game.p2_up = False
        elif message == 'p2key_down_pressed' and player.game.game_type == "local":
            player.game.p2_down = True
        elif message == 'p2key_down_released' and player.game.game_type == "local":
            player.game.p2_down = False


class BasePongConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = None

    def connect(self):
        self.accept()
        self.setup_game()
        if self.game.player1 and self.game.player2:
            self.game.start()
        self.send_connection_message()

    def setup_game(self):
        pass  # Doit être implémenté par les classes dérivées à leurs créations

    def send_connection_message(self):
        user = self.scope['user']
        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'you are connected ' + user.username,
            'data': self.game.__dict__
        }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username

        if message == 'update':
            self.send_update()
        elif 'pressed' in message or 'released' in message:
            self.handle_key_event(message, username)

    def handle_key_event(self, message, username):
        if message == 'key_up_pressed':
            self.game.key_up_pressed(username)
        elif message == 'key_up_released':
            self.game.key_up_released(username)
        elif message == 'key_down_pressed':
            self.game.key_down_pressed(username)
        elif message == 'key_down_released':
            self.game.key_down_released(username)
        elif message == 'p2key_up_pressed' and self.game.game_type == "local":
            self.game.p2_up = True
        elif message == 'p2key_up_released' and self.game.game_type == "local":
            self.game.p2_up = False
        elif message == 'p2key_down_pressed' and self.game.game_type == "local":
            self.game.p2_down = True
        elif message == 'p2key_down_released' and self.game.game_type == "local":
            self.game.p2_down = False
        self.send_debug_message(message)

    def send_debug_message(self, message):
        self.send(text_data=json.dumps({
            'type': 'debug',
            'message': message
        }))

    def send_update(self):
        self.send(text_data=json.dumps({
            'type': 'update received',
            'data': self.game.__dict__
        }))


class PongOnline(BasePongConsumer):
    def setup_game(self):
        user = self.scope['user']
        for game in games_online:
            if not game.has_finished and (game.player1 == user.username or game.player2 == user.username):
                self.game = game
                break
            if not self.game and not game.has_finished and (not game.player1 or not game.player2):
                self.game = game
                if not self.game.player1 and game.player2 != user.username:
                    self.game.player1 = user.username
                elif not self.game.player2 and game.player1 != user.username:
                    self.game.player2 = user.username
                break
        if not self.game:
            self.game = Game(2, "online")
            self.game.player1 = user.username
            games_online.append(self.game)


class PongLocal(BasePongConsumer):
    def setup_game(self):
        user = self.scope['user']
        user1 = user.username
        user2 = user.username + "_2"

        for game in games_local:
            if not game.has_finished and game.player1 == user1 and game.player2 == user2:
                self.game = game
                break
        if not self.game:
            self.game = Game(5, "local")
            self.game.player1 = user1
            self.game.player2 = user2
            games_local.append(self.game)
        else:
            self.game.is_running = True

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        if message == 'setOpponentAlias':
            self.game.player2 = text_data_json['opponent']
        else:
            super().receive(text_data)

class PongOnlineTournament(BasePongConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = None
    def setup_game(self):
        user = self.scope['user'].username
        for tournament in games_tournament:
            if (not tournament.is_finished and not tournament.has_player(user)):
                self.tournament = tournament
                self.tournament.add_player(user)
                break
        if (not self.tournament):
            self.tournament = Tournament()
            self.tournament.add_player(user)
            games_tournament.append(self.tournament)
            self.tournament.start()
    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username

        if message == 'update':
            self.send(text_data=self.tournament.getupdate(username))
        elif 'pressed' in message or 'released' in message:
            self.tournament.handle_key_event(message, username)
