import google.generativeai as genai
from utils.configmap import Config

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        genai.configure(api_key=Config.GEMINI_API_KEY)

    def generate_content(self, prompt):
        return self.model.generate_content(prompt)