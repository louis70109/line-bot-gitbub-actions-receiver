import requests
from utils.configmap import Config

class LineService:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {Config.LINE_CHANNEL_ACCESS_TOKEN}'
        }

    def send_message(self, to, message):
        return requests.post('https://api.line.me/v2/bot/message/push', headers=self.headers, json={
            'to': to,
            'messages': [{'type': 'text', 'text': message}]
        })