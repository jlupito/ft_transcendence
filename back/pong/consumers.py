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
        self.scope['user'].update_from = 'langage save'
        self.scope['user'].save()
        print("Language updated in db: ", language)

    async def set_language(self, language):
        if language in ['english', 'français', 'español']: 
            await self.update_language_in_db(language)

    async def send_language(self):
        language = self.user_profile.language
        await self.send(text_data=json.dumps({'action': 'get_language', 'language': language}))

    async def receive(self, text_data):
        data = json.loads(text_data)
        print("message received in consumer: ", data)
        action = data['action']
        if action == 'get_language':
            await self.send_language()
        if action == 'set_language':
            language = data['language']
            await self.set_language(language)

# ************************* WS POUR LES STATS DES JOUEURS ****************************

class StatsConsumer(AsyncWebsocketConsumer):
    instances = {}

    async def connect(self):
        self.user = self.scope["user"]
        self.instances[self.user.id] = self
        await self.accept()

    async def disconnect(self, close_code):
        del self.instances[self.user.id]

    async def receive(self, text_data):
        pass

    async def send_stats(self, stats):
        print("Sending stats")
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

    def endgame(self):
        self.is_running = False
        self.has_finished = True
        if (self.game_type == "online"):
            new_match = Match.create_match_from_game(self)
            if hasattr(new_match, 'tourn_won'):
                delattr(new_match, 'tourn_won')
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





# ************************* LOGIQUE DU PONG DE BASE ****************************

class BasePongConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game:Game = None

    async def connect(self):
        print("scope: ", self.scope)
        await self.accept()
        await self.setup_game()
        if self.game :
            self.game.start()
            print("appelle send status")
            await self.send_status_update('is_playing')
        await self.send_connection_message()

    async def setup_game(self):
        pass

    async def disconnect(self, close_code):
        await self.send_status_update('is_online')
        print("passe par le disconnect")

    async def send_status_update(self, status):
        await self.channel_layer.group_send(
            "online_users",
            {
                'type': 'status_update',
                'user_id': self.scope['user'].id,
                'status': status
            }
        )
        print("send isplaying ou offline update from:", self.scope['user'].username)

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

# A MODIFIER POUR AJOUTER LA 3e OPTION (faire ca ici ?)
class FriendStatusConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.user_profile = await sync_to_async(UserProfile.objects.get)(username=self.user.username)
            self.user_profile.status = 'is_online'
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
                    'status': 'is_online'
                }
            )
            await self.accept()
        else:
            await self.close()
        print("user is:", self.user_profile)
        print("status is:", self.user_profile.status)

    async def disconnect(self, close_code):
        self.user_profile = await sync_to_async(UserProfile.objects.get)(username=self.user.username)
        self.user_profile.status = 'is_offline'
        print("user is:", self.user_profile)
        print("status is:", self.user_profile.status)
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
        print("receive dans le status consumer")
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
        print("status update event is:", event)


# ************************* CONSUMER ASYNC FRIENDS REQUESTS ****************************

User = get_user_model()

class FriendsRequestsConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.user_profile = await sync_to_async(UserProfile.objects.get)(username=self.user.username)
            await self.channel_layer.group_add(
                "friends_requests",
                self.channel_name
            )
            await self.accept()

            friends_requests = await self.get_friends_requests()
            await self.send(text_data=json.dumps({
                'friends_requests': friends_requests
            }))
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "friends_requests",
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def friends_requests_update(self, event):
        data = {
            'type': 'friends_requests_update',
            'friend_id': event['friend_id'],
            'friend_avatar': event['friend_avatar'],
            'friend_status': event['friend_status'],
            'friend_username': event['friend_username'],
            'friend_stats': event['friend_stats'],
            'friend_joined': event['friend_joined'],
        }
        print('Friebnd Raquest update data is : ', data)
        await self.send(text_data=json.dumps(data))

    async def get_friends_requests(self):
        friend_requests = await sync_to_async(Friend.objects.filter)(receiver=self.user_profile, status='pending')
        return await sync_to_async(self._get_friends_requests)(friend_requests)

    def _get_friends_requests(self, friend_requests):
        return [fr.sender.username for fr in friend_requests]

    async def new_friend_request(self, event):
        data = {
            'type': 'new_friend_request',
            'friend_id': event['friend_id'],
            'friend_avatar': event['friend_avatar'],
            'friend_status': event['friend_status'],
            'friend_username': event['friend_username'],
        }
        print('New friend request data is : ', data)
        await self.send(text_data=json.dumps(data))



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