import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from . import game_instance
import channels.layers
from asgiref.sync import async_to_sync
from django.core.cache import cache

def get_user_count():
    return cache.get('users_count', 0)

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Ajoutez l'utilisateur au groupe de canaux
        await self.channel_layer.group_add("users", self.channel_name)

        # Incrémentez le compteur dans le cache
        cache.add('users_count', 0)
        cache.incr('users_count')

        await self.accept()

    async def disconnect(self, close_code):
        # Retirez l'utilisateur du groupe de canaux
        await self.channel_layer.group_discard("users", self.channel_name)

        # Décrémentez le compteur dans le cache
        cache.decr('users_count')

class ChatConsumer(WebsocketConsumer):
    # def connect(self):

    #     self.accept()

    #     self.send(text_data=json.dumps({
    #         'type':'connection_established',
    #         'message':'You are now connected!'
    #     }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        if (message == 'update'):
            self.send_update()
        if (message == 'key_up_pressed'):
            game_instance.p1_up = True
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p1 up'
            }))
        if (message == 'key_up_released'):
            game_instance.p1_up = False
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p1 up released'
            }))
        if (message == 'key_down_pressed'):
            game_instance.p1_down = True
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p1 down'
            }))
        if (message == 'key_down_released'):
            game_instance.p1_down = False
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p1 down released'
            }))
        if (message == 'p2key_up_pressed'):
            game_instance.p2_up = True
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p2 up pressed'
            }))
        if (message == 'p2key_up_released'):
            game_instance.p2_up = False
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p2 up released'
            }))
        if (message == 'p2key_down_pressed'):
            game_instance.p2_down = True
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p2 down pressed'
            }))
        if (message == 'p2key_down_released'):
            game_instance.p2_down = False
            self.send(text_data=json.dumps({
                'type':'debug',
                'message':'p2 down released'
            }))
        
    
    def send_update(self):
        self.send(text_data=json.dumps({
            'type':'update received',
            'data': game_instance.__dict__
        }))
    