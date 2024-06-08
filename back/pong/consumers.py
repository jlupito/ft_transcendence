import json
from channels.generic.websocket import WebsocketConsumer
import channels.layers
from asgiref.sync import async_to_sync
from django.core.cache import cache
from channels.generic.websocket import WebsocketConsumer
import threading
import time
import websockets
from .models import Match, Tournoi




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
        self.is_running = False

    def to_dict(self):
        return {
            'game_type': self.game_type,
            'delay': self.delay,
            'player1': self.player1,
            'player2': self.player2,
            'WIDTH': self.WIDTH,
            'HEIGHT': self.HEIGHT,
            'paddle_speed': self.paddle_speed,
            'paddle_width': self.paddle_width,
            'paddle_height': self.paddle_height,
            'p1_x_pos': self.p1_x_pos,
            'p1_y_pos': self.p1_y_pos,
            'p2_x_pos': self.p2_x_pos,
            'p2_y_pos': self.p2_y_pos,
            'p1_score': self.p1_score,
            'p2_score': self.p2_score,
            'maxscore': self.maxscore,
            'p1_up': self.p1_up,
            'p1_down': self.p1_down,
            'p2_up': self.p2_up,
            'p2_down': self.p2_down,
            'ball_x_pos': self.ball_x_pos,
            'ball_y_pos': self.ball_y_pos,
            'ball_width': self.ball_width,
            'ball_x_velocity': self.ball_x_velocity,
            'ball_y_velocity': self.ball_y_velocity,
            'ball_x_normalspeed': self.ball_x_normalspeed,
            'has_finished': self.has_finished,
            'is_running': getattr(self, 'is_running', False)
        }

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
        # self.send(text_data=json.dumps({
        #     'message': 'start'
        # }))

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

    def to_dict(self):
        return {
            'name': self.name,
            'player_status': self.player_status,
            'game': self.game.to_dict() if self.game else None
        }

class Tournament():
    def __init__(self):
        self.games = []
        self.players = []
        self.status = "Waiting"
        self.is_finished = False
        self.is_running = True
        self.timer = 10
        self.winner = None
        self.id = len(games_tournament)

    def to_dict(self):
        return {
        'games': [game.to_dict() for game in self.games] if self.games else [],
        'players': [player.to_dict() for player in self.players],
        'status': self.status,
        'is_finished': self.is_finished,
        'is_running': self.is_running,
        'timer': self.timer,
        'winner': self.winner
    }

    def add_player_to_game(self, player):
        game:Game
        for game in self.games:
            if (game.player1 == "" or game.player2 == ""):
                player.game = game
                if (player.game.player1 == ""):
                    player.game.player1 = player.name
                elif (player.game.player2 == ""):
                    player.game.player2 = player.name
                # connecter ici avec la BD pour apairer les joueurs 2 par 2
                break
        if player.game == None:
            player.game = Game(5, "online")
            player.game.player1 = player.name
            self.games.append(player.game)
                
    def run(self):
        # new_tourn = Tournoi.create_tournoi_from_tournament(self)
        # new_tourn.save()
        round = 1
        while self.is_running:
            if self.status == "Waiting":
                if self.timer >= 0 and len(self.players) > 1:
                    time.sleep(1)
                    self.timer -= 1
                elif self.timer < 0:
                    self.status = "Starting"
            if self.status == "Starting":
                for player in self.players:
                    if player.player_status == "Waiting":
                        self.add_player_to_game(player)
                for player in self.players:
                    if not player.game.is_running and player.game.player1 and player.game.player2:
                        player.game.start()
                        player.player_status = "Playing"
                        print(f"Game started for {player.name} with players {player.game.player1} and {player.game.player2}")
                    if player.game.is_running:
                        player.player_status = "Playing"
                self.status = "Started"
            if self.status == "Started":
                for player in self.players:
                    if player.player_status in ["Disqualified", "Qualified"]:
                        continue
                    if player.player_status == "Waiting" and player.game and (player.game.player1 is None or player.game.player2 is None):
                        player.player_status = "Qualified"
                    if player.game and player.game.has_finished and player.game.player1 == player.name:
                        if player.game.p1_score <= player.game.p2_score:
                            player.player_status = "Disqualified"
                        else:
                            player.player_status = "Qualified"
                    elif player.game and player.game.has_finished and player.game.player2 == player.name:
                        if player.game.p2_score <= player.game.p1_score:
                            player.player_status = "Disqualified"
                        else:
                            player.player_status = "Qualified"
                if all(player.player_status in ["Qualified", "Disqualified"] for player in self.players):
                    self.status = "Ending"
            if self.status == "Ending":
                for player in self.players:
                    if player.player_status == "Waiting" and (player.game.player1 is None or player.game.player2 is None):
                        player.player_status = "Winner"
                    if player.game.has_finished and player.game.player1 == player.name:
                        if player.game.p1_score <= player.game.p2_score:
                            player.player_status = "Disqualified"
                        else:
                            player.player_status = "Winner"
                    elif player.game.has_finished and player.game.player2 == player.name:
                        if player.game.p2_score <= player.game.p1_score:
                            player.player_status = "Disqualified"
                        else:
                            player.player_status = "Winner"
                            self.winner = player.name
                if self.winner:
                    self.is_running = False
                    self.is_finished = True
                    self.status = "Finished"
         
    def add_player(self, username):
        if self.status == "Waiting":
            for player in self.players:
                if player.name == username:
                    print(f"Player {username} is already in the tournament.")
                    return
            new_player = Player(username)
            self.players.append(new_player)
            print(f"Added player {username} to the tournament.")

    def start(self):
        thread = threading.Thread(target=self.run)
        thread.start()

    def has_player(self, username):
        for player in self.players:
            if player.name == username:
                return True
        return False

    def getupdate(self, username):
        player:Player
        for player in self.players:
            if (player.name == username):
                return player.game

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
        if self.game and self.game.player1 and self.game.player2:
            self.game.start()
        self.send_connection_message()

    def setup_game(self):
        pass  # Doit être implémenté par les classes dérivées à leurs créations

    def send_connection_message(self):
        user = self.scope['user']
        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'you are connected ' + user.username,
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
        found_tournament = False
        for tournament in games_tournament:
            if not tournament.is_finished and tournament.has_player(user):
                self.tournament = tournament
                self.tournament.add_player(user)
                found_tournament = True
                break
        if not found_tournament:
            for tournament in games_tournament:
                if not tournament.is_finished and tournament.status == "Waiting" and len(tournament.players) < 8:
                    self.tournament = tournament
                    self.tournament.add_player(user)
                    found_tournament = True
                    break
        if not found_tournament:
            self.tournament = Tournament()
            games_tournament.append(self.tournament)
            self.tournament.add_player(user)
            self.tournament.start()

        # Log the tournament and player info for debugging
        print(f"User {user} joined tournament {self.tournament.id}")
        print(f"Current players: {[player.name for player in self.tournament.players]}")



    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username

        if message == 'update':
            tournament_data = {
                'tournament': self.tournament.to_dict(),
                'players': [player.to_dict() for player in self.tournament.players],
                'games': [game.to_dict() for game in self.tournament.games]
            }
            self.send(text_data=json.dumps({
                'type': 'update received',
                'data': tournament_data
            }))
        elif 'pressed' in message or 'released' in message:
            self.tournament.handle_key_event(message, username)