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
    
    def send_update(self):
        self.send(text_data=json.dumps({
            'type':'update received',
            'data': game_instance.__dict__
        }))
    