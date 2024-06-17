import base64
import datetime
import os, re
import requests
import logging

from flask import request
from datetime import datetime
from flask_restful import Resource, abort, reqparse
from linebot.exceptions import InvalidSignatureError
from utils.github import Github
import werkzeug
logger = logging.getLogger(__name__)


class ImageController(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('image', type=werkzeug.datastructures.FileStorage, location='files')
        name = request.form.get('name')
        args = parse.parse_args()
        image_content = args.get('image')

        github = Github()
        res = requests.put(
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {os.getenv('GITHUB')}"
            },
            json={
                "message": '✨ Commit',
                "committer": {"name": "NiJia Lin", "email": os.getenv('EMAIL')},
                "content": f"{base64.b64encode(image_content.read()).decode('ascii')}",
                "branch": "master"},
            url=f"https://api.github.com/repos/{github.repo_name}/contents/images/{name}.png"
        )
        response_msg = res.json()
        return response_msg
        