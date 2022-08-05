import requests, base64, os
from datetime import datetime


class Github():
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
        return res.json()

    def new_or_update_record(self, text: str, today_record: str = None, sha: str = None) -> dict:
        git_url = f"https://api.github.com/repos/{self.repo_name}/contents/{self.file}"

        record = base64.b64decode(today_record).decode('UTF-8')

        if today_record != None:
            text = f'{record}<br />{text}'
        update_sha = {'sha': sha} if sha else {}
        res = requests.put(
            headers={
                "Accept": "application/vnd.github.VERSION.raw",
                "Authorization": f"token {os.getenv('GITHUB')}"
            },
            json={
                "message": f"✨{self.today} Commit",
                "committer": {"name": "NiJia Lin", "email": os.getenv('EMAIL')},
                "content": base64.b64encode(text.encode('UTF-8')).decode('UTF-8'),
                "branch": "master", **update_sha},
            url=git_url
        )
        return res.json()
