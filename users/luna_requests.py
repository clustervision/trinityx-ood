import requests
from config import settings as SETTINGS

class LunaRequestHandler():
    USER_LIST_ENDPOINT = f'{SETTINGS.luna.url}/config/osuser'
    GROUP_LIST_ENDPOINT = f'{SETTINGS.luna.url}/config/osgroup'
    
    @classmethod
    def get_token(cls):
        """
        This method will get the token from the /tmp/token.txt file.
        """
        with open('/tmp/token.txt', 'r') as f:
            token = f.read().strip()
        return token
    
    @classmethod
    def get_auth_header(cls):
        """
        This method will get the authentication header.
        """
        return {'x-access-tokens': cls.get_token()}
    
    def get_users(self):
        """
        This method will get all the users from the database.
        """
        resp = requests.get(self.USER_LIST_ENDPOINT, headers=self.get_auth_header())
        if resp.status_code not in [200, 201, 204]:
            raise Exception(f"Error while getting checks, received status code {resp.status_code}")
        return [{"name":k, **v } for k,v in  resp.json().items()]
    
    def get_groups(self):
        """
        This method will get all the groups from the database.
        """
        resp = requests.get(self.GROUP_LIST_ENDPOINT, headers=self.get_auth_header())
        if resp.status_code not in [200, 201, 204]:
            raise Exception(f"Error while getting checks, received status code {resp.status_code}")
        return [{"name":k, **v } for k,v in  resp.json().items()]

if __name__ == "__main__":
    handler = LunaRequestHandler()
    print(handler.get_users())
    print(handler.get_groups())