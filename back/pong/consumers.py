import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import channels.layers
from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db.models import Q
import threading
import time
from .models import Match, Friend, UserProfile
from django.contrib import messages


# ************************* WS POUR LA LANGUE ******************************
class LanguageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.user_profile = await sync_to_async(UserProfile.objects.get)(username=self.user.username)
            await self.accept()


    @database_sync_to_async
    def update_language_in_db(self, language):
        self.scope['user'].language = language
        self.scope['user'].save()
        # print("Language updated in db: ", language)

    async def set_language(self, language):
        if language in ['english', 'français', 'español']: 
            await self.update_language_in_db(language)
            # await self.send_language()

    async def send_language(self):
        language = self.user_profile.language
        await self.send(text_data=json.dumps({'action': 'get_language', 'language': language}))

    async def receive(self, text_data):
        data = json.loads(text_data)
        # print("message received in consumer: ", data)
        action = data['action']
        if action == 'get_language':
            await self.send_language()
        if action == 'set_language':
            language = data['language']
            await self.set_language(language)

# ************************* WS POUR LES STATS DES JOUEURS ****************************

class StatsConsumer(AsyncWebsocketConsumer):
    instances = {} # Creation d'un dictionnaire vide

    async def connect(self):
        self.user = self.scope["user"]
        self.instances[self.user.id] = self
        await self.accept()

    async def disconnect(self, close_code):
        del self.instances[self.user.id]

    async def receive(self, text_data):
        pass

    async def send_stats(self, stats):
        # print("Sending stats")
        await self.send(text_data=json.dumps(stats))

    @classmethod
    async def send_stats_to_all(cls, stats):
        for consumer in cls.instances.values():
            await consumer.send_stats(stats)

games_online = [] # Création de listes vides
games_local = []
games_tournament_local = []
games_tournament_online = []


# ************************* CLASSE GAME DE BASE ****************************

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
            'is_running': self.is_running
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
            self.p2_score += 1
            self.reset_ball_position()
        if (self.ball_x_pos + self.ball_x_velocity > self.p2_x_pos - self.paddle_width
            and (self.p2_y_pos < self.ball_y_pos + self.ball_y_velocity + self.ball_width < self.p2_y_pos + self.paddle_height + 10)):
            self.ball_x_velocity = -(self.ball_x_velocity + 0.1)
            self.ball_y_velocity = (self.p2_y_pos + self.paddle_height / 2 - self.ball_y_pos) / 16
            self.ball_y_velocity = -self.ball_y_velocity
        elif self.ball_x_pos + self.ball_x_velocity > self.WIDTH:
            self.p1_score += 1
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
        if (self.game_type == "online"):
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


# ************************* CLASSE PLAYER DE BASE ****************************

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


# ************************* LOGIQUE DU TOURNOI ONLINE ****************************

class TournamentOnline():
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
        self.id = len(games_tournament_online)

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
            if player.player_status == "Waiting" and player.game and (player.game.player1 == "" or player.game.player2 == ""): # qualifie le joueur s'il est seul
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
                        winnerProfiles = UserProfile.objects.filter(username=self.winner)
                        winnerProfile = None
                        if winnerProfiles.exists():
                            winnerProfile = winnerProfiles.first()
                            winnerProfile.tourn_won += 1
                            winnerProfile.save()
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
        while self.is_running:
            if self.status == "Waiting":
                self.wait()
            if self.status == "Starting":
                self.starting()
                # for player in self.players:
                #     if player.player_status == "Waiting":
                #         self.add_player_to_game(player, round, current_tourn)
                # for player in self.players:
                #     if not player.game.is_running and player.game.player1 and player.game.player2:
                #         player.game.start()
                #         player.player_status = "Playing"
                #         print(f"Game started for {player.name} with players {player.game.player1} and {player.game.player2}")
                #     if player.game.is_running:
                #         player.player_status = "Playing"
                # self.status = "Started"
            if self.status == "Started":
                self.started()
            if self.status == "Ending":
                self.is_finished = True
                self.is_running = False
                self.status == "Finished"
            time.sleep(0.005)
                # for player in self.players:
                #     if player.player_status == "Waiting" and (player.game.player1 is None or player.game.player2 is None):
                #         player.player_status = "Winner"
                #     if player.game.has_finished and player.game.player1 == player.name:
                #         if player.game.p1_score <= player.game.p2_score:
                #             player.player_status = "Disqualified"
                #         else:
                #             player.player_status = "Winner"
                #     elif player.game.has_finished and player.game.player2 == player.name:
                #         if player.game.p2_score <= player.game.p1_score:
                #             player.player_status = "Disqualified"
                #         else:
                #             player.player_status = "Winner"
                #             self.winner = player.name
                # round+=1
                # if self.winner:
                #     self.is_running = False
                #     self.is_finished = True
                #     self.status = "Finished"
                #     winner_user=User.objects.get(username=self.winner)
                #     winner_userProfile=UserProfile.objects.get(user=winner_user)
                #     winner_userProfile.tourn_won += 1
                #     winner_userProfile.save()

         
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


# ************************* LOGIQUE DU PONG DE BASE ****************************

class BasePongConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game:Game = None

    async def connect(self):
        print("scope: ", self.scope)
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
            await self.game.key_up_pressed(username)
        elif message == 'key_up_released':
            await self.game.key_up_released(username)
        elif message == 'key_down_pressed':
            await self.game.key_down_pressed(username)
        elif message == 'key_down_released':
            await self.game.key_down_released(username)
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

# ************************* SURCHARGE POUR PONG ONLINE ****************************

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


# ************************* SURCHARGE POUR PONG LOCAL ****************************

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

    async def disconnect(self, close_code):
        print("local disconnect")
        user = self.scope['user']
        user1 = user.username
        user2 = user.username + "_2"

        for game in games_local:
            if not game.has_finished and game.player1 == user1 and game.player2 == user2:
                self.game = game
                break
        if (self.game):
            self.game.is_running = False
            self.game.has_finished = True

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        if message == 'opponent_name':
            self.game.player2 = text_data_json['value']
        else:
            await super().receive(text_data)

# ********************* SURCHARGE CLASSE POUR TOURNOI ONLINE ************************

class PongOnlineTournament(BasePongConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = None

    async def setup_game(self):
        user = self.scope['user'].username
        found_tournament = False
        for tournament in games_tournament_online:
            if not tournament.is_finished and await tournament.has_player(user):
                self.tournament = tournament
                await self.tournament.add_player(user)
                found_tournament = True
                break
        if not found_tournament:
            for tournament in games_tournament_online:
                if not tournament.is_finished and tournament.status == "Waiting" and len(tournament.players) < 8:
                    self.tournament = tournament
                    await self.tournament.add_player(user)
                    found_tournament = True
                    break
        if not found_tournament:
            self.tournament = TournamentOnline()
            games_tournament_online.append(self.tournament)
            await self.tournament.add_player(user)
            await self.tournament.start()

        # Log the tournament and player info for debugging
        print(f"User {user} joined tournament {self.tournament.id}")
        print(f"Current players: {[player.name for player in self.tournament.players]}")

    async def disconnect(self, code):
        self.tournament = None

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

# ************************* CLASSE TOURNOI LOCAL ****************************

class TournamentLocal():
    def __init__(self, owner):
        self.game:Game = None
        self.players = []
        self.maxplayer = 0
        self.playername = ""
        self.status = "SelectSize"
        self.is_finished = False
        self.is_running = True
        self.timer = 10
        self.winner = None
        self.id = len(games_tournament_local)
        self.owner = owner
        self.is_started = False

    def prepare_next_match(self):
        if (self.game == None):
            self.game = Game(5, "Local")
        player:Player
        for player in self.players:
            if (self.status == "New_match" and player.player_status == "Waiting"):
                if (self.game.player1 == ""):
                    self.game.player1 = player.name
                    player.game = self.game
                elif (self.game.player2 == ""):
                    self.game.player2 = player.name
                    player.game = self.game
                    while (self.timer > 0):
                        time.sleep(1)
                        self.timer -= 1
                    player.game.start()
                    self.status = "Playing"
                    self.timer = 10
                    break
        if (self.game.is_started == False):
            for player in self.players:
                if (player.name == self.game.player1):
                    player.player_status = "Qualified"
                    self.game = None
                    player.game = None
                    self.status = "End_round"

    def handle_match(self):
        if (not self.game.has_finished):
            return
        player:Player
        for player in self.players:
            if (player.name == self.game.player1):
                if (self.game.p1_score > self.game.p2_score):
                    player.player_status = "Qualified"
                else:
                    player.player_status = "Disqualified"
            elif (player.name == self.game.player2):
                if (self.game.p2_score > self.game.p1_score):
                    player.player_status = "Qualified"
                else:
                    player.player_status = "Disqualified"
        self.game = None
        if not all(player.player_status in ["Qualified", "Disqualified"] for player in self.players):
            self.status = "New_match"
            self.prepare_next_match()
        else:
            self.status = "End_round"

    def next_round(self):
        player:Player
        for player in self.players:
            if (player.player_status == "Qualified"):
                player.player_status = "Waiting"
        count = 0
        for player in self.players:
            if (player.player_status == "Waiting"):
                count += 1
                if (count >= 2):
                    self.status = "New_match"
                    return
        if (count <= 1):
            self.status = "Ended"
            for player in self.players:
                if (player.player_status == "Waiting"):
                    break
            self.winner = player.name
            self.is_finished = True
            self.is_running = False

    def run(self):
        while self.is_running:
            if (self.status == "Adding"):
                pass
            elif (self.status == "New_match"):
                self.prepare_next_match()
            elif (self.status == "Playing"):
                self.handle_match()
            elif (self.status == "End_round"):
                self.next_round()
            time.sleep(0.001)

    async def addPlayers(self, playername):
        player:Player = Player(playername)
        self.players.append(player)

    async def start(self):
        if (self.is_started is not True):
            self.is_started = True
            thread = threading.Thread(target=self.run)
            thread.start()

    async def is_owner(self, user):
        if (user == self.owner):
            return (True)
        else:
            return (False)
    async def to_dict(self):
        return {
        'games': [await self.game.to_dict() if self.game else None],
        'players': [await player.to_dict() for player in self.players],
        'status': self.status,
        'is_finished': self.is_finished,
        'is_running': self.is_running,
        'timer': self.timer,
        'winner': self.winner,
        'maxplayer': self.maxplayer,
        'playername': self.playername
    }

    async def handle_key_event(self, message, username):
        if message == 'key_right_pressed' and self.status == 'SelectSize':
            if (self.maxplayer < 8):
                self.maxplayer += 1
        elif message == 'key_left_pressed' and self.status == 'SelectSize':
            if (self.maxplayer > 0):
                self.maxplayer -= 1
        elif message == 'key_enter_pressed':
            if (self.status == "SelectSize"):
                self.status = "SelectPlayerNames"
        if (self.game == None):
            return
        if message == 'key_up_pressed':
            await self.game.key_up_pressed(self.game.player1)
        elif message == 'key_up_released':
            await self.game.key_up_released(self.game.player1)
        elif message == 'key_down_pressed':
            await self.game.key_down_pressed(self.game.player1)
        elif message == 'key_down_released':
            await self.game.key_down_released(self.game.player1)
        elif message == 'p2key_up_pressed' and self.game.game_type == "Local":
            self.game.p2_up = True
        elif message == 'p2key_up_released' and self.game.game_type == "Local":
            self.game.p2_up = False
        elif message == 'p2key_down_pressed' and self.game.game_type == "Local":
            self.game.p2_down = True
        elif message == 'p2key_down_released' and self.game.game_type == "Local":
            self.game.p2_down = False


# ********************** SURCHARGE CLASSE POUR TOURNOI LOCAL *************************

class PongLocalTournament(BasePongConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = None

    async def setup_game(self):
        user = self.scope['user'].username
        found_tournament = False
        for tournament in games_tournament_local:
            if not tournament.is_finished and await tournament.is_owner(user):
                self.tournament = tournament
                found_tournament = True
                break
        if not found_tournament:
            self.tournament = TournamentLocal(user)
            games_tournament_local.append(self.tournament)
            await self.tournament.start()

    async def handle_key_pressed(self, key):
        if(self.tournament.status == "SelectPlayerNames"):
            if (len(key) == 1 and key[0].isascii() and len(self.tournament.playername) < 15):
                self.tournament.playername += key
            elif (key == "Backspace"):
                self.tournament.playername = self.tournament.playername[:-1]
            elif (key == "Enter"):
                if (self.tournament.playername != ""):
                    player:Player
                    for player in self.tournament.players:
                        if (player.name == self.tournament.playername):
                            return
                    new_player = Player(self.tournament.playername)
                    self.tournament.players.append(new_player)
                    if (len(self.tournament.players) == self.tournament.maxplayer):
                        self.tournament.status = "New_match"
                    self.tournament.playername = ""

    async def disconnect(self, close_code):
        self.tournament = None

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['user'].username
        game_data:Game = self.tournament.game
        if (game_data is not None):
            self.game = game_data
        if message == 'start':
            self.tournament.status = "New_match"
        if message == 'addPlayer':
            if message.startswith('addPlayer'):
                await self.tournament.addPlayers(text_data_json['playername'])
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
        elif message == 'key_pressed' or message == 'key_released':
            await self.handle_key_pressed(text_data_json['key'])
        elif 'pressed' in message or 'released' in message:
            await self.tournament.handle_key_event(message, username)


# ************************* CONSUMER ASYNC ONLINE/OFFLINE/IN_GAME ****************************

# A MODIFIER POUR AJOUTER LA 3e OPTION (faire ca ici ?)
class FriendStatusConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.user_profile = await sync_to_async(UserProfile.objects.get)(username=self.user.username)
            self.user_profile.is_online = True
            await sync_to_async(self.user_profile.save)()
            await self.channel_layer.group_add(
                "online_users",
                self.channel_name
            )
            await self.channel_layer.group_send(
                "online_users",
                {
                    'type': 'status_update',
                    'user_id': self.user.id,
                    'status': 'online'
                }
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        self.user_profile = await sync_to_async(UserProfile.objects.get)(username=self.user.username)
        self.user_profile.is_online = False
        await sync_to_async(self.user_profile.save)()
        await self.channel_layer.group_discard(
            "online_users",
            self.channel_name
        )
        await self.channel_layer.group_send(
            "online_users",
            {
                'type': 'status_update',
                'user_id': self.user.id,
                'status': 'offline'
            }
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'user_id': event['user_id'],
            'status': event['status']
        }))


# ************************* CONSUMER ASYNC FRIENDS REQUESTS ****************************


class FriendsRequestsConsumer(AsyncWebsocketConsumer):
    instances = {} # Creation d'un dictionnaire vide

    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.instances[self.user.id] = self
            # print(f"Added {self.user.username} to instances")
            # print(f"WebSocket for {self.user.username} is now open.")
            await self.accept()
        else:
            print(f"User {self.user.username} is not authenticated")

    async def disconnect(self, close_code):
        if self.user and self.user.id in self.instances:
            del self.instances[self.user.id]
            # print(f"Removed {self.user.username} from instances")
            # print(f"WebSocket for {self.user.username} is now closed.")
        await super().disconnect(close_code)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # print("message received in consumer: ", data)
        inner_data= data['data']
        type = inner_data['type']
        if type == 'send_f_request':
            await self.send_f_updates(inner_data)
        elif type == 'accepted' or type == 'rejected':
            await self.handle_f_updates(inner_data)

    async def send_f_updates(self, data):
        receiver_id = data['receiver_id']
        receiver = await sync_to_async(UserProfile.objects.get)(id=receiver_id)
        sender_id = data['sender_id']
        sender = await sync_to_async(UserProfile.objects.get)(id=sender_id)
        from .views import friends_list
        friends_l = await sync_to_async(friends_list)(sender)
        for friend in friends_l['friends']:
            if friend.username == receiver:
                return
        invite_exists = await sync_to_async(Friend.objects.filter(sender=sender, receiver=receiver, status='pending').first)()
        if invite_exists:
            print("Invite already exists")
            return
        invite_exists = await sync_to_async(Friend.objects.filter(sender=receiver, receiver=sender, status='pending').first)()
        if invite_exists:
            print("Invite already exists")
            return
        await sync_to_async(Friend.objects.create)(sender=sender, receiver=receiver, status='pending')
        
        for user in [receiver, sender]:
            consumer = FriendsRequestsConsumer.instances.get(user.id)
            if consumer:
                # print(f"Sending update to {user.username}")
                await consumer.send(text_data=json.dumps(data))


    async def handle_f_updates(self, data):
        status = data['type']
        receiver_id = data['receiver_id']
        receiver = await sync_to_async(UserProfile.objects.get)(id=receiver_id)
        sender_id = data['sender_id']
        sender = await sync_to_async(UserProfile.objects.get)(id=sender_id)
        inv = await sync_to_async(Friend.objects.filter(sender=receiver, receiver=sender, status='pending').first)()       
         # print(f"friend found: {inv}")
        # print(f"Updating status in consumer to {status}")
        if inv:
            # print("nouvel ami créé")
            inv.status = status
            # print(f"Updating status in consumer to {status}")
            await sync_to_async(inv.save)()
        if status == 'accepted':
            data['rec_avatar'] = receiver.avatar.url
            data['rec_status'] = receiver.is_online
            data['rec_username'] = receiver.username
            data['send_avatar'] = sender.avatar.url
            data['send_status'] = sender.is_online
            data['send_username'] = sender.username
        for user in [receiver, sender]:
            consumer = FriendsRequestsConsumer.instances.get(user.id)
            if consumer:
                # print(f"Sending update to {user.username}")
                await consumer.send(text_data=json.dumps(data))



# ************************* CONSUMER ASYNC USERLIST UPDATE ****************************

class UsersListUpdateConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.user_profile = await sync_to_async(UserProfile.objects.get)(username=self.user.username)
            await self.channel_layer.group_add(
                "userslist_update",
                self.channel_name
            )
            await self.accept()
            new_user = await self.get_new_user()
            await self.channel_layer.group_send(
                "userslist_update",
                {
                    'type': 'userslist_update',
                    'new_user': new_user
                }
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "userslist_update",
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def userslist_update(self, event):
        new_user = event['new_user']
        if self.user.id == new_user['new_user_id']:
            return
        is_friend = await self.is_friend(new_user['new_user_id'])
        if is_friend:
            return
        data = {
            'type': 'userslist_update',
            'new_user': new_user
        }
        await self.send(text_data=json.dumps(data))

    async def get_new_user(self):
        new_user_profile = await sync_to_async(UserProfile.objects.get)(username=self.user.username)
        return await sync_to_async(self._get_new_user)(new_user_profile)

    def _get_new_user(self, new_user_profile):
        return {
            'username': new_user_profile.username,
            'avatar': new_user_profile.avatar.url,
            'new_user_id': new_user_profile.id
        }

    async def is_friend(self, new_user_id):
        friend_exists = await sync_to_async(Friend.objects.filter, thread_sensitive=True)(
            Q(sender=self.user, receiver__id=new_user_id, status='accepted') |
            Q(receiver=self.user, sender__id=new_user_id, status='accepted')
        )
        return await sync_to_async(friend_exists.exists, thread_sensitive=True)()