from config import settings
from pprint import pprint
import requests


class SensuRequestHandler():
    def __init__(self, settings) -> None:
        schema = 'https' if settings.sensu_use_tls else 'http'
        host = settings.sensu_host
        port = settings.sensu_port
        self.sensu_url = f"{schema}://{host}:{port}"

        healthy = self.health_check()
        if not healthy:
            raise ConnectionError(f"Cannot connect to sensu backend at {self.sensu_url}")

    def health_check(self):
        resp = requests.get(f"{self.sensu_url}/health")
        return resp.status_code in [200, 204]

    def get_checks(self):
        resp = requests.get(f"{self.sensu_url}/checks")
        return resp.json()

    def get_events(self):
        resp = requests.get(f"{self.sensu_url}/events")
        return resp.json()

    def get_silenced(self):
        resp = requests.get(f"{self.sensu_url}/silenced")
        return resp.json()


if __name__ == '__main__':
    handler = SensuRequestHandler(settings=settings)
    pprint(handler.get_checks())
    pprint(handler.get_events())
