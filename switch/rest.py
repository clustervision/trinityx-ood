#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This code is part of the TrinityX software suite
# Copyright (C) 2026  ClusterVision Solutions b.v.
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
__copyright__   = "Copyright 2026, Luna2 Project [OOD]"
__license__     = "GPL"
__version__     = "3.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Production"


from configparser import RawConfigParser
import os
import requests
import jwt
import urllib3
from flask import url_for
from log import Log
from constant import INI_FILE, TOKEN_FILE


class Rest():
    """
    All kind of REST Call methods.
    """

    def __init__(self):
        """
        Constructor - Before calling any REST API it will fetch the credentials and endpoint url
        from luna.ini from Luna 2 Daemon.
        """
        self.timeout = 5
        self.response = {"status": False, "status_code": 500, "content": ""}
        self.logger = Log.get_logger()
        self.get_ini_info()
        if str(self.security).lower() in ['y', 'yes', 'true']:
            self.security = True
        else:
            self.security = False
        urllib3.disable_warnings()


    def get_ini_info(self):
        """
        This method will get the information from the INI File.
        """
        self.username, self.password, self.daemon, self.secret_key, self.security, self.protocol = "", "", "", "", "", ""
        self.errors = []
        file_check = os.path.isfile(INI_FILE)
        read_check = os.access(INI_FILE, os.R_OK)
        if file_check is False:
            self.errors.append(f'Luna Configuration File Not Found. Default Path is : {INI_FILE}')
        if read_check is False:
            self.errors.append('Luna Configuration File is not readable.')
        self.logger.debug("INI File => %s READ Check is %s", INI_FILE, read_check)
        if file_check and read_check:
            parser = RawConfigParser()
            parser.read(INI_FILE)
            if parser.has_section('API'):
                self.username = self.get_option(parser, 'API', 'USERNAME')
                self.password = self.get_option(parser, 'API', 'PASSWORD')
                self.secret_key = self.get_option(parser, 'API', 'SECRET_KEY')
                self.protocol = self.get_option(parser, 'API', 'PROTOCOL')
                daemon = self.get_option(parser, 'API', 'ENDPOINT')
                self.daemon = f'{self.protocol}://{daemon}'
                self.security = self.get_option(parser, 'API', 'VERIFY_CERTIFICATE')
            else:
                self.errors.append(f'API section is not found in {INI_FILE}.')
        return self.username, self.password, self.daemon, self.secret_key, self.errors, self.security


    def get_option(self, parser: RawConfigParser, section: str, option: str):
        """
        This method will retrieve the value from the INI
        """
        response: str | None = None
        if parser.has_option(section, option):
            response = parser.get(section, option)
        else:
            self.errors.append(f'{option} is not found in {section} section in {INI_FILE}.')
        return response


    def app_url(self, request):
        """
        Base URL for the SPA shell (window.APP_URL). Must run inside a Flask request context.
        """
        scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
        full_url = f"{scheme}://{request.host}{request.path}"
        full_url = full_url[:-1]
        full_url = f"{full_url}{url_for('home')}"
        return {"APP_URL": full_url}


    def token(self):
        """
        This method will fetch a valid token for further use.
        """
        data = {'username': self.username, 'password': self.password}
        daemon_url = f'{self.daemon}/token'
        self.logger.debug("Token URL => %s", daemon_url)
        try:
            call = requests.post(url=daemon_url, json=data, timeout=self.timeout, verify=self.security)
            self.logger.debug("Response %s & HTTP Code %s", call.content, call.status_code)
            if call.content:
                data = call.json()
                if 'token' in data:
                    response = data['token']
                    if isinstance(TOKEN_FILE, dict):
                        self.errors.append(TOKEN_FILE["error"])
                    else:
                        with open(TOKEN_FILE, 'w', encoding='utf-8') as file_data:
                            file_data.write(response)
                        os.chmod(TOKEN_FILE, mode=0o600)
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
        if isinstance(TOKEN_FILE, dict):
            self.errors.append(TOKEN_FILE["error"])
            return response
        if os.path.isfile(TOKEN_FILE):
            with open(TOKEN_FILE, 'r', encoding='utf-8') as token:
                token_data = token.read()
            try:
                jwt.decode(token_data, str(self.secret_key), algorithms=['HS256'])
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


    def get_data(self, table: str="", name: str=""):
        """
        This method call Luna 2 Daemon via REST API's GET method to fetch the records.
        """
        headers = {'x-access-tokens': self.get_token()}
        daemon_url = f'{self.daemon}/config/{table}'
        if name:
            daemon_url = f'{daemon_url}/{name}'
        self.logger.debug('GET URL => %s', daemon_url)
        try:
            response = requests.get(url=daemon_url, headers=headers, timeout=self.timeout, verify=self.security)
            self.logger.debug('Response %s & HTTP Code %s', response.content, response.status_code)
            data = response.json()
            if isinstance(data, dict) and 'message' in data:
                self.errors.append(data["message"])
                self.response = {"status": False, "status_code": response.status_code, "content": response.json()}
            else:
                self.response = {"status": True, "status_code": response.status_code, "content": response.json()}
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
            self.response = {"status": False, "status_code": 400, "content": f'ERROR :: {ssl_loop_error}'}
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
            self.response = {"status": False, "status_code": 400, "content": f'Request Timeout while {daemon_url}'}
        except requests.exceptions.JSONDecodeError as json_decode_error:
            self.errors.append(f'ERROR :: {json_decode_error}')
            self.response = {"status": False, "status_code": 400, "content": f'ERROR :: {json_decode_error}'}
        return self.response


    def post_data(self, table: str="", name: str="", data: dict | None = None, action: str=""):
        """
        This method call Luna 2 Daemon via REST API's POST method to create/update the records.
        """
        if data is None:
            data = {}
        headers = {'x-access-tokens': self.get_token(), 'Content-Type':'application/json'}
        daemon_url = f'{self.daemon}/config/{table}'
        if name:
            daemon_url = f'{daemon_url}/{name}'
        if action == "clone":
            daemon_url = f'{daemon_url}/_clone'
        self.logger.debug('POST URL => %s', daemon_url)
        self.logger.debug('POST DATA => %s', data)
        try:
            response = requests.post(url=daemon_url, json=data, headers=headers, timeout=self.timeout, verify=self.security)
            self.logger.debug('Response %s & HTTP Code %s', response.content, response.status_code)
            if action == "add":
                if response.status_code == 201:
                    data = response.json()
                    self.response = {"status": True, "status_code": response.status_code, "content": data}
                elif response.status_code == 204:
                    self.response = {"status": False, "status_code": 400, "content": {"message": f"{table.capitalize()} already have {name}."}}
                else:
                    data = response.json()
                    self.response = {"status": False, "status_code": response.status_code, "content": data}
            elif action in ["update", "rename"]:
                if response.status_code == 204:
                    self.response = {"status": True, "status_code": response.status_code, "content": {"message": f"{table.capitalize()} {name} is {action}d successfully."}}
                else:
                    data = response.json()
                    self.response = {"status": False, "status_code": response.status_code, "content": data}
            elif action == "clone":
                data = response.json()
                if response.status_code == 201:
                    self.response = {"status": True, "status_code": response.status_code, "content": data}
                else:
                    self.response = {"status": False, "status_code": response.status_code, "content": data}
            else:
                data = response.json()
                self.response = {"status": False, "status_code": response.status_code, "content": data}
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
            self.response = {"status": False, "status_code": 400, "content": f'ERROR :: {ssl_loop_error}'}
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
            self.response = {"status": False, "status_code": 400, "content": f'Request Timeout while {daemon_url}'}
        except requests.exceptions.JSONDecodeError as json_decode_error:
            self.errors.append(f'ERROR :: {json_decode_error}')
            self.response = {"status": False, "status_code": 400, "content": f'ERROR :: {json_decode_error}'}
        return self.response


    def get_delete(self, table: str="", name: str=""):
        """
        This method is based on REST API's GET method.
        It will delete the records from Luna 2 Daemon
        via REST API's.
        """
        headers = {'x-access-tokens': self.get_token()}
        daemon_url = f'{self.daemon}/config/{table}/{name}/_delete'
        self.logger.debug('GET URL => %s', daemon_url)
        try:
            response = requests.get(url=daemon_url, headers=headers, timeout=self.timeout, verify=self.security)
            self.logger.debug('Response %s & HTTP Code %s', response.content, response.status_code)
            if response.status_code == 204:
                self.response = {"status": True, "status_code": response.status_code, "content": {"message": f"{table.capitalize()} {name} is deleted successfully."}}
            else:
                data = response.json()
                if isinstance(data, dict) and 'message' in data:
                    self.errors.append(data["message"])
                    self.response = {"status": False, "status_code": response.status_code, "content": response.json()}
                else:
                    self.response = {"status": False, "status_code": response.status_code, "content": response.json()}
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
            self.response = {"status": False, "status_code": 400, "content": f'ERROR :: {ssl_loop_error}'}
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
            self.response = {"status": False, "status_code": 400, "content": f'Request Timeout while {daemon_url}'}
        except requests.exceptions.JSONDecodeError as json_decode_error:
            self.errors.append(f'ERROR :: {json_decode_error}')
            self.response = {"status": False, "status_code": 400, "content": f'ERROR :: {json_decode_error}'}
        return self.response
