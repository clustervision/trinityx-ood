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
Microservice Class for the Luna Web.
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2022, Luna2 Project [OOD]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Development"


from configparser import RawConfigParser
import os
import requests
from requests import Session
from requests.adapters import HTTPAdapter
import jwt
import urllib3
from flask import request
from urllib3.util import Retry
from log import Log
from constant import INI_FILE


class Rest():
    """
    All kind of REST Call methods.
    """

    def __init__(self):
        """
        Constructor - Before calling any REST API it will fetch the credentials and endpoint url
        from luna.ini from Luna 2 Daemon.
        """
        if 'X-Forwarded-User' in request.headers:
            if len(request.headers["X-Forwarded-User"]) > 1:
                self.token_file = f'/trinity/home/{request.headers["X-Forwarded-User"]}/.luna-token.dat'
            else:
                self.token_file = '/tmp/.luna-token.dat'
        else:
            self.token_file = '/tmp/.luna-token.dat'
        self.logger = Log.get_logger()
        self.get_ini_info()
        self.security = True if self.security.lower() in ['y', 'yes', 'true']  else False
        urllib3.disable_warnings()
        self.session = Session()
        self.retries = Retry(
            total= 60,
            backoff_factor=0.1,
            status_forcelist=[502, 503, 504],
            allowed_methods={'GET', 'POST'},
        )
        self.session.mount('https://', HTTPAdapter(max_retries=self.retries))


    def get_ini_info(self):
        """
        This method will get the information from the INI File.
        """
        self.username, self.password, self.daemon, self.secret_key, self.security = "", "", "", "", ""
        self.errors = []
        file_check = os.path.isfile(INI_FILE)
        read_check = os.access(INI_FILE, os.R_OK)
        if file_check is False:
            self.errors.append(f'Luna Configuration File Not Found. Default Path is : {INI_FILE}')
        if read_check is False:
            self.errors.append('Luna Configuration File is not readable.')
        self.logger.debug(f'INI File => {INI_FILE} READ Check is {read_check}')
        if file_check and read_check:
            parser = RawConfigParser()
            parser.read(INI_FILE)
            if parser.has_section('API'):
                self.username = self.get_option(parser, 'API', 'USERNAME')
                self.password = self.get_option(parser, 'API', 'PASSWORD')
                self.secret_key = self.get_option(parser, 'API', 'SECRET_KEY')
                protocol = self.get_option(parser, 'API', 'PROTOCOL')
                daemon = self.get_option(parser, 'API', 'ENDPOINT')
                self.daemon = f'{protocol}://{daemon}'
                self.security = self.get_option(parser, 'API', 'VERIFY_CERTIFICATE')
            else:
                self.errors.append(f'API section is not found in {INI_FILE}.')
        return self.username, self.password, self.daemon, self.secret_key, self.errors, self.security


    def get_option(self, parser=None, section=None, option=None):
        """
        This method will retrieve the value from the INI
        """
        response = False
        if parser.has_option(section, option):
            response = parser.get(section, option)
        else:
            self.errors.append(f'{option} is not found in {section} section in {INI_FILE}.')
        return response


    def token(self):
        """
        This method will fetch a valid token for further use.
        """
        data = {'username': self.username, 'password': self.password}
        daemon_url = f'{self.daemon}/token'
        self.logger.debug(f'Token URL => {daemon_url}')
        try:
            call = self.session.post(url=daemon_url, json=data, stream=True, timeout=5, verify=self.security)
            self.logger.debug(f'Response {call.content} & HTTP Code {call.status_code}')
            if call.content:
                data = call.json()
                if 'token' in data:
                    response = data['token']
                    with open(self.token_file, 'w', encoding='utf-8') as file_data:
                        file_data.write(response)
                    os.chmod(self.token_file, mode=0o600)
                elif 'message' in data:
                    self.errors.append(data["message"])
            else:
                self.errors.append(call.content)
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
        except requests.exceptions.JSONDecodeError:
            self.errors.append(call.content)
        return response


    def get_token(self):
        """
        This method will fetch a valid token
        for further use.
        """
        response = False
        if os.path.isfile(self.token_file):
            with open(self.token_file, 'r', encoding='utf-8') as token:
                token_data = token.read()
            try:
                jwt.decode(token_data, self.secret_key, algorithms=['HS256'])
                response = token_data
            except jwt.exceptions.DecodeError:
                self.logger.debug('Token Decode Error, Getting New Token.')
                response = self.token()
            except jwt.exceptions.ExpiredSignatureError:
                self.logger.debug('Expired Signature Error, Getting New Token.')
                response = self.token()
        if response is False:
            response = self.token()
        return response


    def get_data(self, table=None, name=None, data=None):
        """
        This method is based on REST API's GET method.
        It will fetch the records from Luna 2 Daemon
        via REST API's.
        """
        response = False
        headers = {'x-access-tokens': self.get_token()}
        daemon_url = f'{self.daemon}/config/{table}'
        if name:
            daemon_url = f'{daemon_url}/{name}'
        self.logger.debug(f'GET URL => {daemon_url}')
        try:
            call = self.session.get(url=daemon_url, params=data, stream=True, headers=headers, timeout=5, verify=self.security)
            self.logger.debug(f'Response {call.content} & HTTP Code {call.status_code}')
            response_json = call.json()
            if 'message' in response_json:
                self.errors.append(response_json["message"])
            else:
                response = response_json
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
        except requests.exceptions.JSONDecodeError:
            response = False
        return response


    def post_data(self, table=None, name=None, data=None):
        """
        This method is based on REST API's POST method.
        It will post data to Luna 2 Daemon via REST API's.
        And use for creating and updating records.
        """
        response = False
        headers = {
            'x-access-tokens': self.get_token(),
            'Content-Type':'application/json',
            'User-Agent': 'Luna2-web'
        }
        daemon_url = f'{self.daemon}/config/{table}'
        if name:
            daemon_url = f'{daemon_url}/{name}'
        self.logger.debug(f'POST URL => {daemon_url}')
        self.logger.debug(f'POST DATA => {data}')
        try:
            response = self.session.post(url=daemon_url, json=data, stream=True, headers=headers, timeout=5, verify=self.security)
            self.logger.debug(f'Response {response.content} & HTTP Code {response.status_code}')
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
        return response
