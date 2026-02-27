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
Helper Class for the Luna WEB
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2026, Luna2 Project [WEB]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Production"


import hostlist
from flask import url_for
from constant import APP_STATE
from log import Log


class Helper():
    """
    All kind of helper methods.
    """

    def __init__(self):
        """
        Constructor - As of now, nothing have to initialize.
        """
        self.logger = Log.get_logger()


    def app_url(self, request):
        """
        This method will provide the URL's for the frontend application.
        """
        response = {"PROMETHEUS_URL": "", "APP_URL": ""}
        full_url = f"https://{request.host}{request.path}"
        full_url = full_url[:-1]
        full_url_app = f"{full_url}{url_for('home')}"
        base_url = full_url_app[:-1]
        if APP_STATE is False: # FOR Development Only
            promethues_url = full_url.replace("7755", "9090")
        else:
            promethues_url = full_url.replace("8080", "9090")
        response['PROMETHEUS_URL'] = promethues_url
        response['APP_URL'] = base_url
        return response


    def get_hostlist(self, raw_hosts: list) -> dict:
        """
        This method will perform power option on node.
        """
        
        response = {"status": False, "message": "No valid hostlist found."}
        self.logger.info(f'Received hostlist: {raw_hosts}.')
        try:
            result = hostlist.collect_hostlist(raw_hosts)
            self.logger.info(f'Expanded hostlist: {result}.')
            response = {"status": True, "message": result}
        except hostlist.BadHostlist:
            self.logger.info(f'Hostlist is incorrect: {raw_hosts}.')
            response["message"] = f"Hostlist is incorrect: {raw_hosts}."
        return response
