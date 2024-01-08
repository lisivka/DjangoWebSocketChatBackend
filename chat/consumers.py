from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = 'chat_%s' % self.room_name
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            self.accept()
            session = self.scope["session"]
            session_id = session.session_key or session.create()
            # print(f"{self.scope=}")

            async_to_sync(self.send(text_data=json.dumps({
                'event': "Connect",
                'message': f"Connected to room: {self.room_name}",
                'session_id': session_id,
            }))
            )


        except Exception as e:
            async_to_sync(self.send(text_data=json.dumps({
                'event': "Error",
                'message': "Error connect:" + str(e),
            }))
            )

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )
            async_to_sync(self.send(text_data=json.dumps({
                'event': "Connect",
                'message': f"Disconnected from room: {self.room_name}",
            }))
            )

        except Exception as e:
            async_to_sync(self.send(text_data=json.dumps({
                'event': "Error",
                'message': "Error disconnect:" + str(e),
            }))
            )

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            print(f"{text_data_json=}")
            message = text_data_json['message']
            username = text_data_json['username']
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': '[' + self.room_name+ ']' + '[' + username + ']' + " " + message,
                    'username': username,
                }
            )

        except Exception as e:
            async_to_sync(self.send(text_data=json.dumps({
                'event': "Error",
                'message': "Error receive:" + str(e),
            }))
            )

    def chat_message(self, event):
        try:
            message = event['message']
            username = event['username']
            print(f"{event=}")

            self.send(text_data=json.dumps({
                'event': "Send",
                'message': message,
                'username': username,
            }))
        except Exception as e:
            async_to_sync(self.send(text_data=json.dumps({
                'event': "Error",
                'message': "Error chat_message:" + str(e),
            }))
            )
