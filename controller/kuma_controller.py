from datetime import datetime, timedelta
from flask import request
from flask_restful import Resource
from uptime_kuma_api import MonitorStatus

from utils.line_service import LineService
from utils.kuma_service import KumaService
from utils.logging_config import get_logger
from utils.configmap import Config
from utils.gemini_service import GeminiService

logger = get_logger(__name__)


class KumaController(Resource):
    def __init__(self, *args, **kwargs):
        self.gemini_service = GeminiService()
        self.line_service = LineService()
        self.kuma_service = KumaService()
        super().__init__(*args, **kwargs)

    def post(self):
        body = request.get_json()
        msg = body.get('msg')

        if msg:
            prompt = ("你是一位軟體工程師，以下在 Updtime-Kuma status page 當中出現的資訊"
                      "你需要評斷是否解釋給主管與非技術職同事，如果有需要修改或是支援，"
                      "請提供需要幫忙的單位；如果沒有或只是測試訊息，則提出相對建議。")
            response = self.gemini_service.generate_content(
                prompt + "\n log: " + msg)
            logger.info(response.text)
            self.line_service.send_message(Config.ADMIN_LINE_ID, response.text)

        return 'OK'

    def get(self):
        monitors, heart_dict = self.kuma_service.get_monitors()
        name_id_dict = {item['id']: item['name'] for item in monitors}

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
                        prompt = ("Refer to the following error logs, please explain the meaning of these errors in non-technical language, "
                                  "propose possible improvement measures, and indicate whether the assistance of other teams is needed to resolve these issues. "
                                  "The purpose is to report to the project manager and other non-technical stakeholders in Traditional Chinese, "
                                  "assess whether the severity requires reporting.")
                        response = self.gemini_service.generate_content(
                            prompt + "\n" + status_message)
                        logger.info(name_id_dict[monitor_id])
                        logger.info(response.text)
                        return response.text
