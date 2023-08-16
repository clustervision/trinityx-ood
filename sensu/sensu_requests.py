#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file will handle sensu requests.
This file will create flask object and serve the all routes for on demand.
"""

__author__      = 'Diego Sonaglia'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Diego Sonaglia'
__email__       = 'diego.sonaglia@clustervision.com'
__status__      = 'Development'


from pprint import pprint
import requests
from config import sensu_settings


class SensuRequestHandler():
    """
    Sensu request handler
    """
    def __init__(self, sensu_settings) -> None:
        schema = 'https' if sensu_settings.sensu_use_tls else 'http'
        host = sensu_settings.sensu_host
        port = sensu_settings.sensu_port
        self.sensu_url = f"{schema}://{host}:{port}"

        healthy = self.health_check()
        if not healthy:
            raise ConnectionError(f"Cannot connect to sensu backend at {self.sensu_url}")


    def health_check(self):
        """
        This method will perform a health check
        """
        resp = requests.get(f"{self.sensu_url}/health", timeout=10)
        return resp.status_code in [200, 204]


    def get_checks(self):
        """
        This method will get all checks.
        """
        resp = requests.get(f"{self.sensu_url}/checks", timeout=10)
        return resp.json()


    def get_events(self):
        """
        This method will get all events.
        """
        resp = requests.get(f"{self.sensu_url}/events", timeout=10)
        return resp.json()


    def get_silenced(self):
        """
        This method will get all silenced.
        """
        resp = requests.get(f"{self.sensu_url}/silenced", timeout=10)
        return resp.json()


if __name__ == '__main__':
    handler = SensuRequestHandler(sensu_settings=sensu_settings)
    pprint(handler.get_checks())
    pprint(handler.get_events())
