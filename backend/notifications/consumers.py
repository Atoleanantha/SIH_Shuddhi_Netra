# consumers.py
import os
import django
django.setup()
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # Replace with your project name

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Assign a group name for notifications
        self.group_name = 'notifications'
        print("cliend connected")
        # Add this WebSocket connection to the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()  # Accept the connection

    async def disconnect(self, close_code):
        # Remove this WebSocket connection from the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Function to handle messages received via WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        
        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'notification_message',
                'message': message,
            }
        )

    # Function to send notifications to WebSocket clients
    async def notification_message(self, event):
        message = event['message']
        
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
        }))

    # External notification sender function
    @staticmethod
    def send_notification(message):
        """
        Function to send notifications to all WebSocket clients.
        This function is to be called externally from views or elsewhere.
        """
       
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            'notifications',  # Group name
            {
                'type': 'notification_message',
                'message': message,
            }
        )
