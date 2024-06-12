import json
from channels.generic.websocket import AsyncWebsocketConsumer
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
        self.is_started = False
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

    async def to_dict(self):
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
        if (self.is_started is not True):
            self.is_started = True
            thread = threading.Thread(target=self.run)
            thread.start()
        # self.send(text_data=json.dumps({
        #     'message': 'start'
        # }))

    def endgame(self):
        self.is_running = False
        self.has_finished = True
        # print("Final scores: Player 1 =", self.p1_score, ", Player 2 =", self.p2_score)
        new_match = Match.create_match_from_game(self)
        new_match.save()

    async def key_up_pressed(self, username):
        if (username == self.player1):
            self.p1_up = True
        elif (username == self.player2):
            self.p2_up = True
        

    async def key_up_released(self, username):
        if (username == self.player1):
            self.p1_up = False
        elif (username == self.player2):
            self.p2_up = False
    
    async def key_down_pressed(self, username):
        if (username == self.player1):
            self.p1_down = True
        elif (username == self.player2):
            self.p2_down = True
        

    async def key_down_released(self, username):
        if (username == self.player1):
            self.p1_down = False
        elif (username == self.player2):
            self.p2_down = False


class Player:
    def __init__(self, name):
        self.name = name
        self.player_status = 'Waiting'
        self.game:Game = None

    async def to_dict(self):
        return {
            'name': self.name,
            'player_status': self.player_status,
            'game': await self.game.to_dict() if self.game else None
        }

class Tournament():
    def __init__(self):
        self.games = []
        self.players = []
        self.is_started = False
        self.status = "Waiting"
        self.is_finished = False
        self.is_running = True
        self.timer = 10
        self.winner = None
        self.qualif = None
        self.id = len(games_tournament)

    async def to_dict(self):
        return {
        'games': [await game.to_dict() for game in self.games] if self.games else [],
        'players': [await player.to_dict() for player in self.players],
        'status': self.status,
        'is_finished': self.is_finished,
        'is_running': self.is_running,
        'timer': self.timer,
        'winner': self.winner,
        'qualif': self.qualif
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

    def wait(self):
        if self.timer >= 0 and len(self.players) > 1:
            time.sleep(1)
            self.timer -= 1
        elif self.timer < 0:
            self.status = "Starting"
            if (len(self.players) > 4):
                self.qualif = 3
            elif len(self.players) > 2:
                self.qualif = 2
            else:
                self.qualif = 1

    def starting(self):
        for player in self.players:
            if player.player_status == "Waiting":
                self.add_player_to_game(player)
        for player in self.players:
            if player.game and not player.game.is_running and player.game.player1 and player.game.player2:
                player.game.start()
                player.player_status = "Playing"
                print(f"Game started for {player.name} with players {player.game.player1} and {player.game.player2}")
            if player.game and player.game.is_running:
                player.player_status = "Playing"
        self.status = "Started"

    def started(self):
        for player in self.players:
            if player.player_status in ["Disqualified", "Qualified"]:       #parcoure les joueurs, ignore si qualifie/discalifie
                continue
            if player.player_status == "Waiting" and player.game and (player.game.player1 is "" or player.game.player2 is ""): # qualifie le joueur s'il est seul
                player.player_status = "Qualified"
            if player.game and player.game.has_finished and player.game.player1 == player.name:     # Si la partie est finie, regarde le score et determine un gagnant
                if player.game.p1_score <= player.game.p2_score:
                    player.player_status = "Disqualified"
                else:
                    player.player_status = "Qualified"
            elif player.game and player.game.has_finished and player.game.player2 == player.name:   # pareil pour player 2
                if player.game.p2_score <= player.game.p1_score:
                    player.player_status = "Disqualified"
                    player.game = None
                else:
                    player.player_status = "Qualified"
                    player.game = None
        if all(player.player_status in ["Qualified", "Disqualified"] for player in self.players):    #parcours les joueurs, s'ils sont tous qualif/disqualif, rentre dans les conditions
            if (self.qualif == 1):       #finale jouee, donne un gagnant pour le tournois
                self.status = "Ending"
                for player in self.players:
                    player.game = None
                    if (player.player_status == "Qualified"):
                        self.winner = player.name
            else:                       #relance une session de parties
                self.games = []
                for player in self.players:
                    player.game = None
                    if (player.player_status == "Qualified"):
                        player.player_status = "Waiting"
                self.status = "Starting"
                self.qualif -= 1
                self.timer = 10
                while (self.timer >= 0):
                    time.sleep(1)
                    self.timer -= 1

    def run(self):
        # new_tourn = Tournoi.create_tournoi_from_tournament(self)
        # new_tourn.save()
        round = 1
        while self.is_running:
            if self.status == "Waiting":
                self.wait()
            if self.status == "Starting":
                self.starting()
            if self.status == "Started":
                self.started()
            if self.status == "Ending":
                self.is_finished = True
                self.is_running = False
                self.status == "Finished"
            time.sleep(0.005)
         
    async def add_player(self, username):
        if self.status == "Waiting":
            for player in self.players:
                if player.name == username:
                    print(f"Player {username} is already in the tournament.")
                    return
            new_player = Player(username)
            self.players.append(new_player)
            print(f"Added player {username} to the tournament.")

    async def start(self):
        if (self.is_started is not True):
            self.is_started = True
            thread = threading.Thread(target=self.run)
            thread.start()


    async def has_player(self, username):
        for player in self.players:
            if player.name == username:
                return True
        return False

    def getupdate(self, username):
        player:Player
        for player in self.players:
            if (player.name == username):
                return player.game

    async def handle_key_event(self, message, username):
        player:Player
        for player in self.players:
            if (player.name == username):
                break
        if (player == None or player.game == None):
            return
        if message == 'key_up_pressed':
            await player.game.key_up_pressed(username)
        elif message == 'key_up_released':
            await player.game.key_up_released(username)
        elif message == 'key_down_pressed':
            await player.game.key_down_pressed(username)
        elif message == 'key_down_released':
            await player.game.key_down_released(username)
        elif message == 'p2key_up_pressed' and player.game.game_type == "local":
            player.game.p2_up = True
        elif message == 'p2key_up_released' and player.game.game_type == "local":
            player.game.p2_up = False
        elif message == 'p2key_down_pressed' and player.game.game_type == "local":
            player.game.p2_down = True
        elif message == 'p2key_down_released' and player.game.game_type == "local":
            player.game.p2_down = False


class BasePongConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = None

    async def connect(self):
        await self.accept()
        await self.setup_game()
        if self.game and self.game.player1 and self.game.player2:
            self.game.start()
        await self.send_connection_message()

    async def setup_game(self):
        pass

    async def send_connection_message(self):
        user = self.scope['user']
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'you are connected ' + user.username,
        }))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username

        if message == 'update':
            await self.send_update()
        elif 'pressed' in message or 'released' in message:
            await self.handle_key_event(message, username)

    async def handle_key_event(self, message, username):
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
        await self.send_debug_message(message)

    async def send_debug_message(self, message):
        await self.send(text_data=json.dumps({
            'type': 'debug',
            'message': message
        }))

    async def send_update(self):
        await self.send(text_data=json.dumps({
            'type': 'update received',
            'data': self.game.__dict__
        }))


class PongOnline(BasePongConsumer):
    async def setup_game(self):
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
    async def setup_game(self):
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

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        if message == 'setOpponentAlias':
            self.game.player2 = text_data_json['opponent']
        else:
            await super().receive(text_data)

class PongOnlineTournament(BasePongConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = None
    
    async def setup_game(self):
        user = self.scope['user'].username
        found_tournament = False
        for tournament in games_tournament:
            if not tournament.is_finished and await tournament.has_player(user):
                self.tournament = tournament
                await self.tournament.add_player(user)
                found_tournament = True
                break
        if not found_tournament:
            for tournament in games_tournament:
                if not tournament.is_finished and tournament.status == "Waiting" and len(tournament.players) < 8:
                    self.tournament = tournament
                    await self.tournament.add_player(user)
                    found_tournament = True
                    break
        if not found_tournament:
            self.tournament = Tournament()
            games_tournament.append(self.tournament)
            await self.tournament.add_player(user)
            await self.tournament.start()

        # Log the tournament and player info for debugging
        print(f"User {user} joined tournament {self.tournament.id}")
        print(f"Current players: {[player.name for player in self.tournament.players]}")



    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username
        game_data:Game = self.tournament.getupdate(username)
        if (game_data is not None):
            self.game = game_data
        if message == 'update':
            if (game_data is not None):
                game_data = await game_data.to_dict()
            tournament_data = {
                'tournament': await self.tournament.to_dict(),
                # 'players': [await player.to_dict() for player in self.tournament.players],
                # 'games': [await game.to_dict() for game in self.tournament.games],
                'game_data': game_data
            }
            await self.send(text_data=json.dumps({
                'type': 'update received',
                'data': tournament_data
            }))
        elif 'pressed' in message or 'released' in message:
            await self.tournament.handle_key_event(message, username)
                

# ************************* CONSUMER ASYNCHRONE ****************************

from channels.generic.websocket import AsyncWebsocketConsumer

class FriendStatusConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print('connected in FriendStatusConsumer')
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                # print('UserId on connect is', self.user.id),
                    self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"user_{self.user.id}",
            # print('UserId on disconnect is', self.user.id),
                self.channel_name
        )

    # async def receive(self, text_data):  <=== recois les données venant du front sous le format json. Tu peux regarder comment je l'interprête dans mes consumers

    async def status_update(self, event):
        print('status_update in FriendStatusConsumer is running')
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'user_id': event['user_id'],
            'status': event['status']
        }))
