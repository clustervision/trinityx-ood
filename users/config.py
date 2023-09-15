#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file will create the settings.
"""

__author__      = 'Diego Sonaglia'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Diego Sonaglia'
__email__       = 'diego.sonaglia@clustervision.com'
__status__      = 'Development'

import jwt 
import requests
from dynaconf import Dynaconf

TOKEN = None
settings = Dynaconf(
    envvar_prefix="OOD",
    settings_files=[
        "settings/osusers.toml",
        "settings/luna.ini",
        "/trinity/local/ondemand/3.0/config/osusers.toml",
        "/trinity/local/ondemand/3.0/config/luna.ini",
        ],
)
print(settings)
import sys
sys.stdout.flush()
# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.

def get_token():
    """

    This method will fetch a valid token for further use.

    """
    # If there is a token check that is valid and return it 
    if TOKEN is not None:
        try:
            # Try to decode the token to check if it is still valid
            jwt.decode(TOKEN, settings.api.secret_key, algorithms=['HS256'])
            return TOKEN
        except jwt.exceptions.ExpiredSignatureError:
            # If the token is expired is ok, we fetch a new one
            pass

    # Otherwise just fetch a new one
    data = {'username': settings.api.username, 'password': settings.api.password}
    daemon_url = f'{settings.api.protocol}://{settings.api.endpoint}/token'
    response = requests.post(daemon_url, json=data, stream=True, timeout=3, verify=(settings.api.verify_certificate.lower() == 'true'))
    token = response.json()['token']
    return token