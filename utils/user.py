import os
import requests
import json


class User:
    def __init__(self) -> None:
        self.url = os.getenv('PARSE_URL')+'/classes/users'
        self.headers = {
        "X-Parse-Application-Id": f"{os.getenv('PARSE_APPID')}",
        "X-Parse-REST-API-Key": f"{os.getenv('REST_API_KEY')}"
    }

    def _get(self, uid='', params=None):
        # 'where={"playerName":"Sean Plott","cheatMode":false}' 
        req = requests.get(self.url+'/'+uid, headers=self.headers,
        params={"where": params})

        print(req.json())
        return req

    def _post(self, user_obj: dict):
        req = requests.post(self.url, headers=self.headers, data=json.dumps(user_obj))
        return req

    def get_user(self, uid='', where=None):
        return self._get(uid, params=where)

    def create_user(self):
        # requests.post(url=self.url)
        pass

    def update_user(self):
        pass
