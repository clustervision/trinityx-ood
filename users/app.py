#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is main file. It will create flask object and serve the API's.
"""

__author__      = 'Diego Sonaglia'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Diego Sonaglia'
__email__       = 'diego.sonaglia@clustervision.com'
__status__      = 'Development'

from flask import Flask, render_template
from config import settings
import requests

app = Flask(__name__, static_url_path='/')

class OsUserRequestHandler():
    USER_LIST_ENDPOINT = '/config/osusers'
    GROUP_LIST_ENDPOINT = '/config/osgroups'
    
    @classmethod
    def get_token(cls):
        """
        This method will get the token from the /tmp/token.txt file.
        """
        with open('/tmp/token.txt', 'r') as f:
            token = f.read().strip()
        return token
    
    @classmethod
    def get_auth_header(cls):
        """
        This method will get the authentication header.
        """
        return {'x-access-tokens': cls.get_token()}
    
    @classmethod
    def get_users(cls):
        """
        This method will get all the users from the database.
        """
        response = requests.get(auth=cls.get_auth_header(), url=settings.API_URL + cls.USER_LIST_ENDPOINT)


@app.route("/")
def index():
    """
    This is main route of application, it will serve index page of the application.
    """
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
