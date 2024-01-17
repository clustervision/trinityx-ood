#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This code is part of the TrinityX software suite
# Copyright (C) 2023  ClusterVision Solutions b.v.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

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
from base.config import settings

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
    SENSU_URL = "http://localhost:4567"
    print(SENSU_URL)
    handler = SensuRequestHandler(sensu_url=SENSU_URL)
    pprint(handler.get_checks())
    pprint(handler.get_events())
