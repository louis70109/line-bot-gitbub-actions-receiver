import logging
import os
import requests
import google.generativeai as genai
from uptime_kuma_api import UptimeKumaApi, MonitorStatus
from datetime import datetime, timedelta
from flask import request
from flask_restful import Resource
from linebot import (LineBotApi)
from linebot.models import (
    TextSendMessage)

logger = logging.getLogger(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))


class KumaController(Resource):

    def __init__(self, *args, **kwargs):
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=self.gemini_key)

        super().__init__(*args, **kwargs)

    def post(self):
        body = request.get_json()

        msg = body.get('msg')
        if msg is not None:
            prompt = "你是一位軟體工程師，以下在 Updtime-Kuma status page 當中出現的資訊你需要評斷是否解釋給主管與非技術職同事，如果有需要修改或是支援，請提供需要幫忙的單位；如果沒有或只是測試訊息，則提出相對建議。"
            response = self.model.generate_content(prompt+"\n log: "+msg)
            logger.info(response.text)
            res = requests.post('https://api.line.me/v2/bot/message/push', headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {os.getenv("LINE_CHANNEL_ACCESS_TOKEN")}'},
                json={
                    'to': os.getenv('ADMIN_LINE_ID'),
                    'messages': [{'type': 'text', 'text': response.text}]
            })
        return 'OK'

    def get(self):

        kuma_account = os.getenv('KUMA_ACCOUNT')
        kuma_password = os.getenv('KUMA_PASSWORD')

        with UptimeKumaApi('https://YOURDOMAIN/') as api:
            api.login(kuma_account, kuma_password)

            name_id_dict = {item['id']: item['name']
                            for item in api.get_monitors()}

            # print(name_id_dict)
            heart_dict = api.get_important_heartbeats()
            for idx in heart_dict:
                for heart in heart_dict[idx]:
                    if heart['status'] == MonitorStatus.DOWN:
                        monitor_id = heart['monitorID']
                        status_message = f"Module: {name_id_dict[monitor_id]}\nError message: {heart['msg']}"

                        given_time = datetime.strptime(
                            heart['time'], '%Y-%m-%d %H:%M:%S.%f')

                        now = datetime.now()

                        time_difference = now - given_time

                        if time_difference < timedelta(days=5):
                            prompt = "Refer to the following error logs, please explain the meaning of these errors in non-technical language, propose possible improvement measures, and indicate whether the assistance of other teams is needed to resolve these issues. The purpose is to report to the project manager and other non-technical stakeholders in Traditional Chinese, assess whether the severity requires reporting."
                            response = self.model.generate_content(
                                prompt+"\n"+status_message)
                            print(name_id_dict[monitor_id])
                            print(response.text)
