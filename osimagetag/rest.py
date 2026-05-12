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
from flask import jsonify
from requests import Session
from requests.adapters import HTTPAdapter
import jwt
import urllib3
from urllib3.util import Retry
from log import Log
from constant import INI_FILE, TOKEN_FILE


class Rest():
    """
    All kind of REST Call methods.
    """

    @staticmethod
    def forward_daemon_response(resp):
        """Map a requests.Response (or falsy) to a Flask response (same contract as osimage app)."""
        if resp is False or resp is None:
            return jsonify({
                "status": False,
                "content": {"message": "No response from daemon"},
            }), 200
        if not resp.content:
            return '', resp.status_code
        try:
            body = resp.json()
        except ValueError:
            return jsonify({
                "message": "Daemon returned non-JSON body",
                "status_code": resp.status_code,
                "body": (resp.text or "").strip(),
            }), resp.status_code if not resp.ok else 200
        return jsonify(body), resp.status_code

    @staticmethod
    def app_url(request):
        """Base URL for the SPA (window.APP_URL). Uses script_root so OOD sub-URIs like /pun/sys/... work."""
        root = (getattr(request, "host_url", None) or "").rstrip("/")
        if not root:
            root = f"{request.scheme}://{request.host}".rstrip("/")
        sr = (getattr(request, "script_root", None) or request.environ.get("SCRIPT_NAME") or "").rstrip("/")
        response = {"APP_URL": (root + sr) if sr else root}
        return response

    def __init__(self):
        """
        Constructor - Before calling any REST API it will fetch the credentials and endpoint url
        from luna.ini from Luna 2 Daemon.
        """
        self.logger = Log.get_logger()
        self.get_ini_info()
        # VERIFY_CERTIFICATE may be missing in INI; get_option can return bool False — never call .lower() on that.
        sec = self.security
        if isinstance(sec, bool):
            sec = 'true' if sec else ''
        elif sec is None:
            sec = ''
        else:
            sec = str(sec).strip()
        self.security = True if sec.lower() in ['y', 'yes', 'true'] else False
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
        response = False
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
        if os.path.isfile(TOKEN_FILE):
            with open(TOKEN_FILE, 'r', encoding='utf-8') as token:
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
        if not getattr(self, 'daemon', None) or not str(self.daemon).strip().startswith(('http://', 'https://')):
            hint = '; '.join((self.errors or [])[-8:]) or 'check [API] PROTOCOL, ENDPOINT in luna.ini'
            return {
                "status": False,
                "content": {"message": f'Daemon base URL not configured ({INI_FILE}). {hint}'},
            }
        daemon_url = f'{self.daemon}/config/{table}'
        if name:
            daemon_url = f'{daemon_url}/{name}'
        self.logger.debug(f'GET URL => {daemon_url}')
        call = None
        try:
            tok = self.get_token()
            if not tok:
                return {
                    "status": False,
                    "content": {"message": "Luna token unavailable (check luna.ini API credentials and daemon /token)."},
                }
            headers = {'x-access-tokens': tok}
            call = self.session.get(url=daemon_url, params=data, stream=True, headers=headers, timeout=5, verify=self.security)
            self.logger.debug(f'Response {call.content} & HTTP Code {call.status_code}')
            response_json = call.json()
            if isinstance(response_json, dict) and 'message' in response_json:
                self.errors.append(response_json["message"])
            response = response_json
            if (
                isinstance(response, dict)
                and 'message' in response
                and 'status' not in response
            ):
                response = {"status": False, "content": {"message": str(response.get("message", ""))}}
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
            response = {"status": False, "content": {"message": f'ERROR :: {ssl_loop_error}'}}
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
            response = {"status": False, "content": {"message": f'Request Timeout while {daemon_url}'}}
        except requests.exceptions.JSONDecodeError:
            preview = ""
            code = "?"
            if call is not None:
                preview = (call.text or "")[:800]
                code = call.status_code
            self.errors.append(f'Non-JSON from daemon {daemon_url}: {preview[:200]}')
            response = {
                "status": False,
                "content": {"message": f'Daemon returned non-JSON (HTTP {code}). {preview[:500]}'},
            }
        except Exception as ex:
            self.errors.append(str(ex))
            response = {"status": False, "content": {"message": f'GET {daemon_url} failed: {ex}'}}
        return response


    def post_data(self, table=None, name=None, data=None):
        """
        This method is based on REST API's POST method.
        It will post data to Luna 2 Daemon via REST API's.
        And use for creating and updating records.
        """
        response = False
        headers = {'x-access-tokens': self.get_token(), 'Content-Type':'application/json'}
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


    def get_delete(self, table=None, name=None):
        """
        This method is based on REST API's GET method.
        It will delete the records from Luna 2 Daemon
        via REST API's.
        """
        response = False
        headers = {'x-access-tokens': self.get_token()}
        daemon_url = f'{self.daemon}/config/{table}/{name}/_delete'
        self.logger.debug(f'GET URL => {daemon_url}')
        try:
            response = self.session.get(url=daemon_url, stream=True, headers=headers, timeout=5, verify=self.security)
            self.logger.debug(f'Response {response.content} & HTTP Code {response.status_code}')
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
        return response


    def post_clone(self, table=None, name=None, data=None):
        """
        This method is based on REST API's POST method.
        It will post data to Luna 2 Daemon via REST API's.
        And use for cloning the records.
        """
        response = False
        headers = {'x-access-tokens': self.get_token(), 'Content-Type':'application/json'}
        daemon_url = f'{self.daemon}/config/{table}/{name}/_clone'
        self.logger.debug(f'Clone URL => {daemon_url}')
        try:
            response = self.session.post(url=daemon_url, json=data, stream=True, headers=headers, timeout=5, verify=self.security)
            self.logger.debug(f'Response {response.content} & HTTP Code {response.status_code}')
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
        return response


    def get_status(self, table=None, name=None, data=None):
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
        self.logger.debug(f'Status URL => {daemon_url}')
        try:
            call = self.session.get(url=daemon_url, params=data, stream=True, headers=headers, timeout=5, verify=self.security)
            self.logger.debug(f'Response {call.content} & HTTP Code {call.status_code}')
            response = call.status_code
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
        return response


    def get_raw(self, route=None, uri=None):
        """
        This method is based on REST API's GET method.
        It will fetch the records from Luna 2 Daemon
        via REST API's.
        """
        response = False
        headers = {'x-access-tokens': self.get_token()}
        daemon_url = f'{self.daemon}/{route}'
        if uri:
            daemon_url = f'{daemon_url}/{uri}'
        self.logger.debug(f'RAW URL => {daemon_url}')
        try:
            response = self.session.get(url=daemon_url, stream=True, headers=headers, timeout=5, verify=self.security)
            self.logger.debug(f'Response {response.content} & HTTP Code {response.status_code}')
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
        return response


    def post_raw(self, route=None, payload=None):
        """
        This method is based on REST API's GET method.
        It will fetch the records from Luna 2 Daemon
        via REST API's.
        """
        response = False
        headers = {'x-access-tokens': self.get_token(), 'Content-Type':'application/json'}
        daemon_url = f'{self.daemon}/{route}'
        self.logger.debug(f'Clone URL => {daemon_url}')
        try:
            response = self.session.post(url=daemon_url, json=payload, stream=True, headers=headers, timeout=5, verify=self.security)
            self.logger.debug(f'Response {response.content} & HTTP Code {response.status_code}')
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
        return response


    def get_url_data(self, route=None, payload=None):
        """
        This method is based on REST API's GET method.
        It will fetch the records from Luna 2 Daemon
        via REST API's.
        """
        response = False
        try:
            response = self.session.get(url=route, stream=True, data=payload, timeout=5, verify=self.security)
            self.logger.debug(f'Response {response.content} & HTTP Code {response.status_code}')
        except requests.exceptions.SSLError as ssl_loop_error:
            self.errors.append(f'ERROR :: {ssl_loop_error}')
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {route}')
        return response
