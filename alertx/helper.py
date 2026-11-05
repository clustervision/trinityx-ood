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
from time import time
from urllib.parse import urlparse, urlunparse
import requests
import urllib3
from flask import url_for
from constant import ALERT_MANAGER_DIR
from log import Log

urllib3.disable_warnings()

SCHEME_CACHE_TTL = 600
scheme_cache = {}


class Helper():
    """
    All kind of helper methods.
    """

    def __init__(self):
        """
        Constructor - As of now, nothing have to initialize.
        """
        self.logger = Log.get_logger()


    def detect_protocol(self, host, port, timeout=2):
        """
        Prometheus/Alert Manager TLS is configured independently of the OOD portal
        and the Luna daemon, so probe the port directly instead of assuming either
        scheme applies. Results are cached so pages do not re-probe on every load.
        """
        now = time()
        cached = scheme_cache.get((host, port))
        if cached and cached[1] > now:
            return cached[0]
        try:
            requests.get(f"https://{host}:{port}/", timeout=timeout, verify=False)
            scheme = "https"
        except requests.exceptions.RequestException:
            try:
                requests.get(f"http://{host}:{port}/", timeout=timeout)
                scheme = "http"
            except requests.exceptions.RequestException:
                scheme = "https"
        scheme_cache[(host, port)] = (scheme, now + SCHEME_CACHE_TTL)
        return scheme


    def app_url(self, request=None):
        """
        This method will provide the URL's for the frontend application.
        """
        response = {"PROMQL_URL": "", "APP_URL": "", "ALERT_URL": ""}
        scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
        full_url = f"{scheme}://{request.host}{request.path}"
        full_url = full_url[:-1]
        full_url_app = f"{full_url}{url_for('home')}"
        APP_URL = full_url_app[:-1]
        hostname = request.host.split(':')[0]
        promql_scheme = self.detect_protocol(hostname, 9090)
        PROMQL_URL = f"{promql_scheme}://{hostname}:9090"
        response['PROMQL_URL'] = PROMQL_URL
        response['APP_URL'] = APP_URL
        credentials = self.get_alert_manager_credential()
        if isinstance(credentials, dict):
            alert_scheme = self.detect_protocol(hostname, 9093)
            raw_url = f"{alert_scheme}://{hostname}:9093/api/v2/alerts"
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

