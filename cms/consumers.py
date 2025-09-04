import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.serializers.json import DjangoJSONEncoder


class AdminNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "admin_notifications"
        if self.channel_layer is not None:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if self.channel_layer is not None:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Optionally handle messages from the client
        pass

    async def send_notification(self, event):
        notification = event["notification"]
        await self.send(text_data=json.dumps(notification, cls=DjangoJSONEncoder))

    @database_sync_to_async
    def get_latest_notifications(self):
        from cms.models.notification import AdminNotification
        from cms.serializers.notification import AdminNotificationSerializer

        qs = AdminNotification.objects.order_by("-created_at")[:10]
        return AdminNotificationSerializer(qs, many=True).data
