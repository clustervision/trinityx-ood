#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
import jwt
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
        self.logger = Log.get_logger()
        self.get_ini_info()


    def get_ini_info(self):
        """
        This method will get the information from the INI File.
        """
        self.username, self.password, self.daemon, self.secret_key = "", "", "", ""
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
            else:
                self.errors.append(f'API section is not found in {INI_FILE}.')
        return self.username, self.password, self.daemon, self.secret_key, self.errors


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
            call = requests.post(url=daemon_url, json=data, timeout=5)
            self.logger.debug(f'Response {call.content} & HTTP Code {call.status_code}')
            if call.content:
                data = call.json()
                if 'token' in data:
                    response = data['token']
                    with open(TOKEN_FILE, 'w', encoding='utf-8') as file_data:
                        file_data.write(response)
                elif 'message' in data:
                    self.errors.append(data["message"])
            else:
                self.errors.append(call.content)
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


    def get_raw(self, route=None, uri=None):
        """
        This method is based on REST API's GET method.
        It will fetch the records from Luna 2 Daemon
        via REST API's.
        """
        response = False
        headers = {'x-access-tokens': self.get_token(), 'User-Agent': 'Luna2-web'}
        daemon_url = f'{self.daemon}/{route}'
        if uri:
            daemon_url = f'{daemon_url}/{uri}'
        self.logger.debug(f'RAW URL => {daemon_url}')
        try:
            response = requests.get(url=daemon_url, headers=headers, timeout=5)
            self.logger.debug(f'Response {response.content} & HTTP Code {response.status_code}')
        except requests.exceptions.ConnectionError:
            self.errors.append(f'Request Timeout while {daemon_url}')
        return response
