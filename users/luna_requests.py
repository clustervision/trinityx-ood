import requests
from config import settings as SETTINGS

class LunaRequestHandler():
    endpoints = {
        'users': {
            'list': f'{SETTINGS.luna.url}/config/osuser',
            'get': f'{SETTINGS.luna.url}/config/osuser/{{name}}',
            'update': f'{SETTINGS.luna.url}/config/osuser/{{name}}',
            'delete': f'{SETTINGS.luna.url}/config/osuser/{{name}}/_delete'
        },
        'groups': {
            'list': f'{SETTINGS.luna.url}/config/osgroup',
            'get': f'{SETTINGS.luna.url}/config/osgroup/{{name}}',
            'update': f'{SETTINGS.luna.url}/config/osgroup/{{name}}',
            'delete': f'{SETTINGS.luna.url}/config/osgroup/{{name}}/_delete'
        }
    }

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

    def list(self, target):
        """
        This method will get all the groups/users from the database.
        """
        resp = requests.get(self.endpoints[target]['list'], headers=self.get_auth_header())
        if resp.status_code not in [200, 201, 204]:
            raise Exception(f"Error while listing {target}, received status code {resp.status_code}")
        return  resp.json()

    def get(self, target, name):
        """
        This method will get the group/user from the database.
        """
        resp = requests.get(self.endpoints[target]['get'].format(name=name), headers=self.get_auth_header())
        if resp.status_code not in [200, 201, 204]:
            raise Exception(f"Error while getting {target}, received status code {resp.status_code}")
        return  resp.json()



if __name__ == "__main__":
    handler = LunaRequestHandler()
