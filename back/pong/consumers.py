import json
from channels.generic.websocket import WebsocketConsumer
from . import game_instance

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.send(text_data=json.dumps({
            'type':'connection_established',
            'message':'You are now connected!'
        }))

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
    