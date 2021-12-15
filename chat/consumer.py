# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer,WebsocketConsumer
from asgiref.sync import async_to_sync

from django.contrib.auth import get_user_model
User=get_user_model()
from chat.models import Message

class ChatConsumer(WebsocketConsumer):
    
    def fetch_messages(self,data):
        # message=Message.last_10_messages()
        message=Message.objects.all()
        content={
            "message":self.messages_to_json(message)
        }
        # self.send_chat_message(content)
        self.send_message(content)
    
    def new_message(self,data):
        print("in new_message")
        auther=data["from"]
        auther_user=User.objects.filter(username=auther)[0]
        message=Message.objects.create(auther=auther_user,content=data['message'])
        content={"command":'new_message',"message":self.message_to_json(message)}
        return self.send_chat_message(content)
    def messages_to_json(self,messages):
        result=[]
        for msg in messages:
            result.append(self.message_to_json(msg))
        return result
    
    def message_to_json(self,message):
        return {"auther":message.auther.username,
                "content":message.content,
                "timestamp":str(message.timestamp)}
    commands={
        "fetch_messages":fetch_messages,
        "new_message":new_message
    }
    def connect(self):
        print("in connect")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        ))

        self.accept()

    def disconnect(self, close_code):
        print("in disconnect")
        # Leave room group
        async_to_sync(self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        ))

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self,data)
        
        
        
    def send_chat_message(self,message):
        print("in send_chat_message")
        # message = data['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        ))
    
    def send_message(self,message):
        print("in send message")
        self.send(text_data=json.dumps(message))
    # Receive message from room group
    def chat_message(self, event):
        print("in chat message")
        message = event['message']
        # Send message to WebSocket
        async_to_sync(self.send(text_data=json.dumps({message})))