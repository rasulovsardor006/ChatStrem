import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'video_{self.room_name}'
        self.user_id = str(id(self))  # Har bir ulanish uchun unikal ID

        # Xonaga qo'shilish
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Foydalanuvchiga o'z ID'sini yuborish
        await self.send(text_data=json.dumps({
            'type': 'user_id',
            'data': self.user_id
        }))

        # Boshqa foydalanuvchilarga yangi foydalanuvchi qo'shilganini xabar qilish
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'sender': self.user_id
            }
        )

    async def disconnect(self, close_code):
        # Xonadan chiqish
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Boshqa foydalanuvchilarga foydalanuvchi chiqib ketganini xabar qilish
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'sender': self.user_id
            }
        )

    async def receive(self, text_data):
        message = json.loads(text_data)
        message_type = message.get('type')
        message_data = message.get('data')
        sender = message.get('sender')
        target = message.get('target')

        # Xabarni boshqa foydalanuvchilarga yuborish
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': message_type,
                'data': message_data,
                'sender': sender,
                'target': target
            }
        )

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'sender': event['sender']
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'sender': event['sender']
        }))

    async def offer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'data': event['data'],
            'sender': event['sender'],
            'target': event['target']
        }))

    async def answer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'data': event['data'],
            'sender': event['sender'],
            'target': event['target']
        }))

    async def ice_candidate(self, event):
        await self.send(text_data=json.dumps({
            'type': 'ice-candidate',
            'data': event['data'],
            'sender': event['sender'],
            'target': event['target']
        }))