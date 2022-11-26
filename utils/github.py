import logging
import requests, base64, os
from datetime import datetime
logger = logging.getLogger(__name__)

class Github:
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.repo_name = 'louis70109/ideas-tree'  # change to your repo name
        self.file = self.today + '.md'

    def get_record(self) -> dict:
        git_url = f"https://api.github.com/repos/{self.repo_name}/contents/{self.file}"
        res = requests.get(
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"token {os.getenv('GITHUB')}"
            },
            url=git_url
        )
        if res.status_code >= 400:
            logger.debug(f'❌ GitHub repo record is None. Info: {res.json()}')

        return res.json()

    def new_or_update_record(self, text: str, today_record: str = None, sha: str = None) -> dict:
        git_url = f"https://api.github.com/repos/{self.repo_name}/contents/{self.file}"

        text = self.markdown_to_html(text)

        update_sha = {}
        # If contain SHA, means content exist.
        if sha != None:
            record = base64.b64decode(today_record).decode('UTF-8')
            text = f'{record}<br />{text}'
            update_sha = {'sha': sha}

        res = requests.put(
            headers={
                "Accept": "application/vnd.github.VERSION.raw",
                "Authorization": f"token {os.getenv('GITHUB')}"
            },
            json={
                "message": f"✨{self.today} Commit",
                "committer": {"name": "NiJia Lin", "email": os.getenv('EMAIL')},
                "content": base64.b64encode(text.encode('UTF-8')).decode('utf-8'),
                "branch": "master", **update_sha},
            url=git_url
        )
        if res.status_code >= 400:
            logger.warning(f'❌ GitHub Record create || update fail. Info: {res.json()}')
            return None
        return res.json()

    @staticmethod
    def markdown_to_html(contents):
        res = requests.post(headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {os.getenv('GITHUB')}"
        }, url="https://api.github.com/markdown",
        json={"text": contents})
        
        if res.status_code == 200:
            return res.text
        if res.status_code>=400:
            logger.warning(f'❌ Markdown format error. Info: {res.json()}')
            return None
    
    @staticmethod
    def record_judgement():
        pass