import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TelemetryConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time telemetry streaming.

    Clients connect to ``ws/telemetry/<drone_id>/`` and receive live
    telemetry updates pushed via the channel layer group.
    """

    async def connect(self):
        """Join the drone-specific telemetry group and accept the connection."""
        self.drone_id = self.scope['url_route']['kwargs']['drone_id']
        self.group_name = f'telemetry_{self.drone_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Leave the telemetry group on disconnect."""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def telemetry_update(self, event):
        """Handle incoming telemetry update and forward to WebSocket client."""
        await self.send(text_data=json.dumps(event['data']))
