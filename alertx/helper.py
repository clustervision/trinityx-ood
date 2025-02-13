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
Helper Class for the AlertX.
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2025, TrinityX[AlertX]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Development"

import os
from urllib.parse import urlparse, urlunparse
from flask import url_for
from constant import APP_STATE, ALERT_MANAGER_DIR
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


    def app_url(self, request=None):
        """
        This method will provide the URL's for the frontend application.
        """
        response = {"PROMQL_URL": "", "APP_URL": "", "ALERT_URL": ""}
        full_url = f"https://{request.host}{request.path}"
        full_url = full_url[:-1]
        full_url_app = f"{full_url}{url_for('home')}"
        APP_URL = full_url_app[:-1]
        if APP_STATE is False: # FOR Development Only
            PROMQL_URL = full_url.replace("7755", "9090")
        else:
            PROMQL_URL = full_url.replace("8080", "9090")
        response['PROMQL_URL'] = PROMQL_URL
        response['APP_URL'] = APP_URL
        credentials = self.get_alert_manager_credential()
        if isinstance(credentials, dict):
            raw_url = PROMQL_URL.replace("9090", "9093")
            raw_url = f"{raw_url}/api/v2/alerts"
            parsed_url = urlparse(raw_url)
            ALERT_URL = urlunparse((
                parsed_url.scheme,
                f"{credentials['user']}:{credentials['password']}@{parsed_url.netloc}",
                parsed_url.path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
            response['ALERT_URL'] = ALERT_URL
        else:
            response['ALERT_URL'] = f"ERROR :: {credentials}"
        return response


    def get_alert_manager_credential(self):
        """
        This method will provide the alert manager credentials.
        """
        credentials = ""
        if not os.path.isdir(ALERT_MANAGER_DIR):
            credentials = f"Directory '{ALERT_MANAGER_DIR}' does not exist."
        try:
            files = [f for f in os.listdir(ALERT_MANAGER_DIR) if os.path.isfile(os.path.join(ALERT_MANAGER_DIR, f))]
        except Exception as e:
            files = []
            credentials = f"ERROR :: Unable to read the files in '{ALERT_MANAGER_DIR}' :: {str(e)}"
            return credentials
        if len(files) == 1:
            file_name, _ = os.path.splitext(files[0])
            file_path = os.path.join(ALERT_MANAGER_DIR, files[0])
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            if not content:
                credentials = f"File '{file_path}' is empty."
            else:
                credentials =  {"user": file_name, "password": content}
        else:
            credentials = f"Expected 1 file, but found {len(files)} files in '{ALERT_MANAGER_DIR}'."
        return credentials

