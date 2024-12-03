import json
from channels.generic.websocket import AsyncWebsocketConsumer
import os
import uuid
import asyncio
#from chat.database import insert_into_bd,start_bd
from http import cookies
import requests
from requests.auth import HTTPBasicAuth
from huggingface_hub import InferenceClient
from .utils import *


hist=dict([])

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.client_id = self.scope['url_route']['kwargs']['client_id']
        if self.client_id not in hist:
            hist[self.client_id] = []
        await self.accept()

    async def disconnect(self, close_code):
        if self.client_id in hist:
            del hist[self.client_id]
        print(f"Connection closed for client {self.client_id}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        hist[self.client_id].append({"role": "user", "content": message})
        language = data['language']
        value = data["value"]
        formatted_message = f"You: {message}"

        if value == "Meta_Llama_3_1_70B_Instruct":
            response = await ask_Meta_Llama_3_1_70B_Instruct_async(message, self.client_id)
        elif value == "Mixtral_8x7B":
            response = await ask_Mixtral_8x7B_async(message, self.client_id)
        elif value == "Mixtral_8x22b":
            response = await ask_Mixtral_8x22b_async(message, self.client_id)
        elif value == "Gemma_7b":
            response = await ask_Gemma_7b_async(message, self.client_id)

#       На случай возвращения старых моделей или добавлени я новых:
#       elif value == "chatgpt":
#       elif value == "Mistral_7B_Instruct":
#       elif value == "Mistral_Nemo_Instruct":
#       elif value == "Mixtral_8x22b":

        answer = f"Assistant: {response}"
        print(answer)
        print(f"Received message from client {self.client_id}: {message}")
        print(language)
        print(value)
        print(hist[self.client_id])

        # Отправляем сообщения отдельно как сырой текст
        await self.send(text_data=formatted_message)
        await self.send(text_data=answer)
