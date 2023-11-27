import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Users,Message,Connection

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'connection_room'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()


    def receive(self, text_data):
        connection=Connection.objects.order_by('-id')[0]
        sender=Users.objects.get(id=connection.user1.id)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        Message.objects.create(content=message,sender=sender,connection=connection).save()
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message
            }
        )

    def chat_message(self, event):
        message = event['message']
       

        self.send(text_data=json.dumps({
            'type':'chat',
            'message':message
        }))

