import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import CampaignMessage

class CampaignChatConsumer(WebsocketConsumer):
    def connect(self):
        self.campaign_id = self.scope['url_route']['kwargs']['campaign_id']
        self.room_group_name = f'chat_{self.campaign_id}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json.get('content')
        user = self.scope.get('user')
        
        if content and user and user.is_authenticated:
            message = CampaignMessage.objects.create(
                campaign_id=self.campaign_id,
                sender=user,
                content=content
            )

            sender_name = getattr(user, 'first_name', '') + ' ' + getattr(user, 'last_name', '')
            sender_name = sender_name.strip() or getattr(user, 'username', 'User')

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'content': message.content,
                    'sender_name': sender_name,
                    'created_at': message.created_at.isoformat()
                }
            )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'content': event['content'],
            'sender_name': event['sender_name'],
            'created_at': event['created_at']
        }))
