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
from config import settings

class SensuRequestHandler():
    """
    Sensu request handler
    """
    def __init__(self, sensu_url) -> None:
        self.sensu_url = sensu_url

    def get_checks(self):
        """
        This method will get all checks.
        """
        resp = requests.get(f"{self.sensu_url}/checks", timeout=10)
        if resp.status_code not in [200, 201, 204]:
            raise Exception(f"Error while getting checks, received status code {resp.status_code}")
        return resp.json()


    def get_events(self):
        """
        This method will get all events.
        """
        resp = requests.get(f"{self.sensu_url}/events", timeout=10)
        if resp.status_code not in [200, 201, 204]:
            raise Exception(f"Error while getting events, received status code {resp.status_code}")
        return resp.json()


    def get_silenced(self):
        """
        This method will get all silenced.
        """
        resp = requests.get(f"{self.sensu_url}/silenced", timeout=10)
        if resp.status_code not in [200, 201, 204]:
            raise Exception(f"Error while getting silenced, received status code {resp.status_code}")
        return resp.json()


if __name__ == '__main__':
    print(settings.sensu.url)
    handler = SensuRequestHandler(sensu_url=settings.sensu.url)
    pprint(handler.get_checks())
    pprint(handler.get_events())
