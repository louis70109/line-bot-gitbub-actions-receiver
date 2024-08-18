import base64
import datetime
import os
import re
import requests
import logging
from flask import request
from datetime import datetime
from flask_restful import Resource, abort
from utils.github import Github
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApiBlob,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)


handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

configuration = Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
)
logger = logging.getLogger(__name__)


class LineController(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self):
        body = request.get_data(as_text=True)
        signature = request.headers['X-Line-Signature']

        # get request body as text
        body = request.get_data(as_text=True)
        logger.info("Request body: " + body)

        # parse webhook body
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)
        return 'OK'

    @handler.add(MessageEvent, message=ImageMessageContent)
    def handle_github_message(event):
        image_content = b''
        with ApiClient(configuration) as api_client:
            line_bot_blob_api = MessagingApiBlob(api_client)
            message_content = line_bot_blob_api.get_message_content(
                event.message.id)
            image_content = message_content
            # for chunk in message_content.iter_content():
            #     image_content += chunk

        github = Github()
        res = requests.put(
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {os.getenv('GITHUB')}"
            },
            json={
                "message": f'✨ Commit {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                "committer": {"name": "NiJia Lin", "email": os.getenv('EMAIL')},
                "content": f"{base64.b64encode(image_content).decode('ascii')}",
                "branch": "master"},
            url=f"https://api.github.com/repos/{github.repo_name}/contents/images/{event.message.id}.png"
        )
        response_msg = res.json().get('content').get('html_url')

        # TODO: move to github.py
        record = github.get_record()
        sha = record.get('sha')
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            user = line_bot_api.get_profile(user_id=event.source.user_id)

        text = f"<br /><img src='{response_msg}' width=450 height=450>"
        if record.get('content') is None:
            text = f"<h2><img src='{user.picture_url}' width=30 height=30>{user.display_name}</h2><br /><img src='{response_msg}' width=450 height=450>"

        modify_record = github.new_or_update_record(
            text, today_record=record.get('content'),
            sha=sha)
        status_message = "✅" if modify_record else "❌"
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(ReplyMessageRequest(
                replyToken=event.reply_token,
                messages=[TextMessage(
                    text=f'{status_message}\n📝https://github.com/{github.repo_name}/blob/master/{datetime.now().strftime("%Y-%m-%d")}.md')]
            ))

    @handler.add(MessageEvent, message=TextMessageContent)
    def handle_github_actions_message(event):
        text = event.message.text

        # message must be: "ReRun OWNER/REPO RUN_ID"
        if re.match("ReRun\s+\w+\/(\w+\W+)*[0-9]+", text):
            repo_info = text.split(" ")
            logger.info(repo_info)
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
                reply_text = f'🧐 Please validate repo || run id, {res.json()}'
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                ))
        elif text == '入口':
            reply_text = '- QRC: https://custom-qrcode-lpdaqdezra-zf.a.run.app\n* Bot: https://lin.ee/pNz6HA5\n\n攝影機: https://lin.ee/YlaqS0t\n\n行事曆: https://lin.ee/92O5Od8'
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)

                line_bot_api.reply_message(ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                ))
        else:
            github = Github()
            record = github.get_record()
            sha = record.get('sha')
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                user = line_bot_api.get_profile(user_id=event.source.user_id)

            # TODO: move to github.py
            if record.get('content') is None:
                text_html = github.markdown_to_html(text)
                text = f"<h2><img src='{user.picture_url}' width=30 height=30>{user.display_name}</h2><br />{text_html}"
            modify_record = github.new_or_update_record(
                text, today_record=record.get('content'),
                sha=sha)
            status_message = "✅" if modify_record else "❌"
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message(ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[
                        TextMessage(
                            text=f'{status_message}\n📝https://github.com/{github.repo_name}/blob/master/{datetime.now().strftime("%Y-%m-%d")}.md')
                    ]
                ))
