import logging
import requests
import base64
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class Github:
    BASE_URL = "https://api.github.com"
    
    def __init__(self, repo_name='louis70109/ideas-tree'):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.repo_name = repo_name
        self.file = f"{self.today}.md"
        self.token = os.getenv('GITHUB')
        self.email = os.getenv('EMAIL')

    def _headers(self, accept="application/vnd.github+json"):
        return {
            "Accept": accept,
            "Authorization": f"token {self.token}"
        }

    def _get_git_url(self, endpoint):
        return f"{self.BASE_URL}/repos/{self.repo_name}/contents/{endpoint}"

    def get_record(self) -> dict:
        url = self._get_git_url(self.file)
        res = requests.get(headers=self._headers(), url=url)
        
        if res.status_code >= 400:
            logger.debug(f'❌ GitHub repo record is None. Info: {res.json()}')
            return {}
        
        return res.json()

    def new_or_update_record(self, text: str, today_record: str = None, sha: str = None) -> dict:
        url = self._get_git_url(self.file)
        text = self.markdown_to_html(text)
        
        if sha:
            record = base64.b64decode(today_record).decode('UTF-8')
            text = f'{record}<br />{text}'

        payload = {
            "message": f"✨{self.today} Commit",
            "committer": {"name": "NiJia Lin", "email": self.email},
            "content": base64.b64encode(text.encode('UTF-8')).decode('utf-8'),
            "branch": "master"
        }
        
        if sha:
            payload['sha'] = sha

        res = requests.put(headers=self._headers("application/vnd.github.VERSION.raw"), json=payload, url=url)
        
        if res.status_code >= 400:
            logger.warning(f'❌ GitHub Record create || update fail. Info: {res.json()}')
            return None
        
        return res.json()

    @staticmethod
    def markdown_to_html(contents):
        url = f"{Github.BASE_URL}/markdown"
        res = requests.post(headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {os.getenv('GITHUB')}"
        }, url=url, json={"text": contents})

        if res.status_code == 200:
            return res.text
        
        logger.warning(f'❌ Markdown format error. Info: {res.json()}')
        return None
