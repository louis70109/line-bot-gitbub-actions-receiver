from uptime_kuma_api import UptimeKumaApi
from utils.configmap import Config

class KumaService:
    def __init__(self):
        self.api_url = Config.KUMA_API_URL
        self.account = Config.KUMA_ACCOUNT
        self.password = Config.KUMA_PASSWORD

    def get_monitors(self):
        with UptimeKumaApi(self.api_url) as api:
            api.login(self.account, self.password)
            return api.get_monitors(), api.get_important_heartbeats()