# ws/consumers.py
from src.settings import CHANNEL_LAYERS
from src.models import Project

from channels.generic.websocket import AsyncWebsocketConsumer
import json
import jwt
from asgiref.sync import sync_to_async
import logging

# Add a new method to ChannelLayer
# We can send message to client with client_id instead of channel_name
from django.utils.module_loading import import_string
async def send_by_client_id(channel_layer, client_id, message):
    try:
        for channel_name in channel_layer.client_map[client_id]:
            await channel_layer.send(channel_name, {
                "type": "send_message",
                "message": message,
            })
    except Exception as e:
        logging.error(e)
        pass

ChannelLayer = import_string(CHANNEL_LAYERS["default"]["BACKEND"])
ChannelLayer.send_by_client_id = send_by_client_id


class WSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        token = self.scope["url_route"]["kwargs"]["token"]

        try:
            # secret_key = Project.objects.get(id=self.project_id).secret_key
            secret_key = (await sync_to_async(Project.objects.get)(id=self.project_id)).secret_key
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            self.client_id = payload["client_id"]
            if "sendable" in payload:
                self.sendable = payload["sendable"]
            else:
                self.sendable = True
            await self.channel_layer.group_add(self.project_id, self.channel_name)

            if hasattr(self.channel_layer, "client_map"):
                self.channel_layer.client_map[self.client_id].add(self.channel_name) # multiple login from same user
            else:
                self.channel_layer.client_map = {self.client_id: {self.channel_name}}

            await self.accept()

            ip = self.scope["client"][0]
            logging.info(f"IP: {ip} - New connection to {self.project_id} from {self.client_id}")
        except Exception as e:
            logging.error(e)
            await self.close()


    async def disconnect(self, close_code):
        try:
            self.channel_layer.client_map[self.client_id].remove(self.channel_name)
            self.channel_layer.group_discard(self.project_id, self.channel_name)
        except:
            pass


    async def receive(self, text_data):
        if not self.sendable:
            return
        text_data_json = json.loads(text_data)
        if "receivers" in text_data_json: # send to specific user
            receivers = text_data_json["receivers"]

            if not isinstance(receivers, list): # if receivers is not list
                receivers = [receivers] # convert to list of one element

            for recipient in receivers:
                await self.channel_layer.send_by_client_id(
                    recipient,
                    {
                        "sender": self.client_id,
                        "message": text_data_json["message"],
                    }
                )
        else: # send to all users if receivers is not specified
            await self.channel_layer.group_send(
                self.project_id,
                {
                    "type": "send_message",
                    "message": {
                        "sender": self.client_id,
                        "message": text_data_json["message"],
                    }
                },
            )


    async def send_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))
