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
import toml
from base.ini import Ini
from base.token import Token


LUNA_CONFIG_PATH = "/trinity/local/ondemand/3.0/config/luna.ini"
INFINIBAND_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "settings", "app.toml")

def get_app_configs():
    """
    This method will read the configuration file and return the settings.
    """
    config = toml.load(INFINIBAND_CONFIG_PATH)
    return config

def get_luna_configs():
    """
    This method will read the configuration file and return the settings.
    """
    config = Ini.read_ini(LUNA_CONFIG_PATH)
    return config

def get_env_configs():
    config = {}
    for key, value in os.environ.items():
        if key.startswith("OOD_"):
            config[key[5:]] = value
    return config

def get_configs():
    """
    This method will read the configuration file and return the settings.
    """
    configs = {
        "LUNA": get_luna_configs(),
        "APP": get_app_configs(),
        "ENV": get_env_configs()
    }
    return configs

def get_token():
    """

    This method will fetch a valid token for further use.

    """
    config = get_luna_configs()

    token = Token.get_token(
        config['USERNAME'],
        config['PASSWORD'],
        config['PROTOCOL'],
        config['ENDPOINT'],
        config['VERIFY_CERTIFICATE']
    )    
    return token

def get_luna_endpoint():
    """
    This method will return the luna endpoint.
    """
    config = Ini.read_ini(LUNA_CONFIG_PATH)
    return f"{config['PROTOCOL']}://{config['ENDPOINT']}"

def get_verify_certificate():
    """
    This method will return the verify certificate.
    """
    config = Ini.read_ini(LUNA_CONFIG_PATH)
    return config['VERIFY_CERTIFICATE']
