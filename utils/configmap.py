import os

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    ADMIN_LINE_ID = os.getenv('ADMIN_LINE_ID')
    KUMA_ACCOUNT = os.getenv('KUMA_ACCOUNT')
    KUMA_PASSWORD = os.getenv('KUMA_PASSWORD')
    KUMA_API_URL = os.getenv('KUMA_API_URL')