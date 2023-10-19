# ws/consumers.py
from src.settings import CHANNEL_LAYERS
from src.models import Project, Domain
from src.funks import validate_domain

from channels.generic.websocket import AsyncWebsocketConsumer
import json
import jwt
from asgiref.sync import sync_to_async
import logging

# Add a new method to ChannelLayer
# We can send message to client with client_id instead of channel_name
from django.utils.module_loading import import_string


async def send_by_client_id(channel_layer, client_id, message, sender_channel_name=None):
    try:
        for channel_name in channel_layer.client_map[client_id]:
            await channel_layer.send(
                channel_name,
                {
                    "type": "send_message",
                    "message": message,
                    "sender_channel_name": sender_channel_name,
                },
            )
    except Exception as e:
        logging.error(e)
        pass


ChannelLayer = import_string(CHANNEL_LAYERS["default"]["BACKEND"])
ChannelLayer.send_by_client_id = send_by_client_id
ChannelLayer.client_map = {}


class WSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.project = self.scope["url_route"]["kwargs"]["project"]
            token = self.scope["url_route"]["kwargs"]["token"]
            project = await sync_to_async(Project.objects.get)(name=self.project)

            for key, value in self.scope["headers"]:
                if key.decode("utf-8") == "origin":
                    if value.decode("utf-8") == "null":
                        await self.close()
                        return
                    else:
                        domain = value.decode("utf-8")
                        domain, _ = validate_domain(domain)
                        break
            else:
                domain = "Unknown"

            if not project.allow_any_domains:
                if not await sync_to_async(lambda domain, project: Domain.objects.filter(domain=domain, project=project).exists())(domain, project):
                    logging.error(
                        f"Domain: {domain} - Project: {self.project} - Not found"
                    )
                    await self.close()
                    return
            
            payload = jwt.decode(token, project.secret_key, algorithms=["HS256"])
            if "id" not in payload:
                await self.close()
                return
            for key, value in payload.items():
                setattr(self, key, value)
            self.client_id = f"{self.project}_{self.id}"
            await self.channel_layer.group_add(self.project, self.channel_name)

            if self.client_id in self.channel_layer.client_map:
                self.channel_layer.client_map[self.client_id].add(self.channel_name)
            else:
                self.channel_layer.client_map[self.client_id] = {self.channel_name}

            await self.accept()

            ip = self.scope["client"][0]
            logging.info(
                f"IP: {ip} - Domain: {domain} - Project: {self.project} - Client: {self.client_id} - Connected"
            )
        except Exception as e:
            logging.error(e)
            await self.close()

    async def disconnect(self, close_code):
        try:
            self.channel_layer.client_map[self.client_id].remove(
                self.channel_name
            )
            self.channel_layer.group_discard(self.project, self.channel_name)
        except:
            pass

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            if "receivers" in text_data_json:  # send to specific user
                receivers = text_data_json["receivers"]

                if not isinstance(receivers, list):  # if receivers is not list
                    receivers = [receivers]  # convert to list of one element

                for id in receivers:
                    await self.channel_layer.send_by_client_id(
                        client_id=f"{self.project}_{id}",
                        message={
                            "sender": self.id,
                            "message": text_data_json["message"],
                        },
                        sender_channel_name=self.channel_name,
                    )
            else:  # send to all users if receivers is not specified
                await self.channel_layer.group_send(
                    self.project,
                    {
                        "type": "send_message",
                        "message": {
                            "sender": self.id,
                            "message": text_data_json["message"],
                        },
                        "sender_channel_name": self.channel_name,
                    },
                )
        except:
            pass

    async def send_message(self, event):
        if event["sender_channel_name"] != self.channel_name:
            await self.send(text_data=json.dumps(event["message"]))
