# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AnswerNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.form_id = self.scope['url_route']['kwargs']['form_id']
        self.room_group_name = f'form_{self.form_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_answer(self, event):
        answer_data = event['answer_data']
        await self.send(text_data=json.dumps(answer_data))
