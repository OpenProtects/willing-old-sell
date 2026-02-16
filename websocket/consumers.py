import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = None
        self.room_group_name = None
        
        token = self.scope.get('query_string', b'').decode().split('token=')[-1].split('&')[0] if self.scope.get('query_string') else None
        
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                self.user = await self.get_user(user_id)
            except (InvalidToken, TokenError, KeyError):
                pass
        
        if self.user:
            self.room_group_name = f'user_{self.user.id}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'ping':
            await self.send(text_data=json.dumps({'type': 'pong'}))
    
    async def notification_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data']
        }))
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'data': event['data']
        }))
    
    async def order_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'order',
            'data': event['data']
        }))
    
    async def wishlist_match(self, event):
        await self.send(text_data=json.dumps({
            'type': 'wishlist',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = None
        
        token = self.scope.get('query_string', b'').decode().split('token=')[-1].split('&')[0] if self.scope.get('query_string') else None
        
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                self.user = await self.get_user(user_id)
            except (InvalidToken, TokenError, KeyError):
                pass
        
        if self.user:
            has_access = await self.check_room_access()
            if has_access:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
            else:
                await self.close()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            content = data.get('content', '')
            if content.strip():
                message = await self.save_message(content)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message_broadcast',
                        'data': message
                    }
                )
        elif message_type == 'ping':
            await self.send(text_data=json.dumps({'type': 'pong'}))
        elif message_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_broadcast',
                    'user_id': self.user.id,
                    'username': self.user.username
                }
            )
    
    async def chat_message_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'data': event['data']
        }))
    
    async def typing_broadcast(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username']
            }))
    
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def check_room_access(self):
        from chat.models import ChatRoom
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.user1_id == self.user.id or room.user2_id == self.user.id
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        from chat.models import ChatRoom, ChatMessage
        from django.utils import timezone
        
        room = ChatRoom.objects.get(id=self.room_id)
        message = ChatMessage.objects.create(
            room=room,
            sender=self.user,
            content=content
        )
        room.updated_at = timezone.now()
        room.save(update_fields=['updated_at'])
        
        return {
            'id': message.id,
            'sender_id': self.user.id,
            'sender_name': self.user.username,
            'sender_avatar': self.user.avatar,
            'content': content,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
