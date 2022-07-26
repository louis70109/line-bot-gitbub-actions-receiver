import os
from flask import request
from flask_restful import Resource, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage)
import requests

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))


class LineIconSwitchController(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self):
        body = request.get_data(as_text=True)
        signature = request.headers['X-Line-Signature']

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            print("Invalid signature. Please check your channel access token/channel secret.")
            abort(400)

        return 'OK'

    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(event):
        text = event.message.text
        # message must be: "OWNER REPO RUN_ID"
        repo_info = text.split(" ")
        print(repo_info)
        res = requests.post(
            headers={
                "Accept":"application/vnd.github+json",
                "Authorization": f"token {os.getenv('GITHUB')}"
            },
            url=f"https://api.github.com/repos/{repo_info[0]}/actions/runs/{repo_info[1]}/rerun"
            )
        if res.status_code == 201:
            line_bot_api.reply_message(
                event.reply_token,
                messages=TextSendMessage(text=f"https://github.com/{repo_info[0]}/actions/runs/{repo_info[1]}")
            )
