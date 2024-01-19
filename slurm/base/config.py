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
This file will create the settings.
"""

__author__ = "Diego Sonaglia"
__copyright__ = "Copyright 2022, Luna2 Project[OOD]"
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "ClusterVision Solutions Development Team"
__email__ = "support@clustervision.com"
__status__ = "Development"

import os
import sys
import jwt
import requests
from dynaconf import Dynaconf

TOKEN = None
settings = Dynaconf(
    envvar_prefix="OOD",
    settings_files=[
        os.path.join(os.path.dirname(__file__), "settings", "slurm.toml"),
        os.path.join(os.path.dirname(__file__), "settings", "luna.ini"),
        os.path.join(os.path.dirname(__file__), "..", "settings", "slurm.toml"),
        os.path.join(os.path.dirname(__file__), "..", "settings", "luna.ini"),
        "/trinity/local/ondemand/3.0/config/slurm.toml",
        "/trinity/local/ondemand/3.0/config/luna.ini",
    ],
)


def get_token():
    """

    This method will fetch a valid token for further use.

    """
    # If there is a token check that is valid and return it
    if TOKEN is not None:
        try:
            # Try to decode the token to check if it is still valid
            jwt.decode(TOKEN, settings.api.secret_key, algorithms=["HS256"])
            return TOKEN
        except jwt.exceptions.ExpiredSignatureError:
            # If the token is expired is ok, we fetch a new one
            pass

    # Otherwise just fetch a new one
    data = {"username": settings.api.username, "password": settings.api.password}
    daemon_url = f"{settings.api.protocol}://{settings.api.endpoint}/token"
    response = requests.post(
        daemon_url,
        json=data,
        stream=True,
        timeout=3,
        verify=(settings.api.verify_certificate.lower() == "true"),
    )
    token = response.json()["token"]
    return token


def get_luna_url():
    """

    This method will return the luna url.

    """
    return f"{settings.api.protocol}://{settings.api.endpoint}"
