import datetime
import os, re
from flask import request
from datetime import datetime

from flask_restful import Resource, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage)
import requests

from utils.github import Github

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

        # message must be: "ReRun OWNER/REPO RUN_ID"
        if re.match("ReRun\s+\w+\/(\w+\W+)*[0-9]+", text):
            repo_info = text.split(" ")
            print(repo_info)
            res = requests.post(
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"token {os.getenv('GITHUB')}"
                },
                url=f"https://api.github.com/repos/{repo_info[1]}/actions/runs/{repo_info[2]}/rerun"
            )

            if res.status_code == 201:
                reply_text = f"✅ Re-Run success\nhttps://github.com/{repo_info[1]}/actions/runs/{repo_info[2]}"
            else:
                reply_text = '🧐 Please validate repo || run id'
            line_bot_api.reply_message(
                event.reply_token,
                messages=TextSendMessage(text=reply_text)
            )
        else:
            github = Github()
            record = github.get_record()
            sha = record.get('sha')
            user = line_bot_api.get_profile(user_id=event.source.user_id)

            # First message add User profile
            if record.get('content') == None:
                text = f"<h2><img src='{user.picture_url}' width=30 height=30>{user.display_name}</h2><br />{text}"
            modify_record = github.new_or_update_record(text, today_record=record.get('content'),
                                                        sha=sha)
            # print(modify_record.get('html'))
            status_message = "✅" if modify_record else "❌"
            line_bot_api.reply_message(
                event.reply_token,
                messages=TextSendMessage(
                    text=f'{status_message}\n📝https://github.com/{github.repo_name}/blob/master/{datetime.now().strftime("%Y-%m-%d")}.md')
            )
