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
Constant File for the Luna Web.
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2022, Luna2 Project [OOD]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Development"

import os

home_dir = os.path.expanduser("~")
if os.path.exists(home_dir) and os.access(home_dir, os.R_OK | os.W_OK):
    TOKEN_FILE = f"{home_dir}/.luna-token.dat"
else:
    TOKEN_FILE = {
        "error": f"The home directory '{home_dir}' does not exist or lacks read/write permissions."
    }

INI_FILE = '/trinity/local/ondemand/3.0/config/luna.ini'
LICENSE = '/trinity/local/ondemand/3.0/LICENSE.txt'
LOG_DIR = '/var/log/luna'
LOG_FILE = '/var/log/luna/luna2-web.log'
EDITOR_KEYS = ['options', 'content', 'comment', 'prescript', 'partscript', 'postscript']
TEMPERATURE_URL = "https://localhost:9090/api/v1/query?query=max+by+(hostname%2C+luna_group)+(ipmi_temperature_celsius{+name%3D~%22[cC][pP][uU].*[tT][eE][mM][pP].*%22+})"
SYSTEM_LOAD_URL = "https://localhost:9090/api/v1/query?query=avg+by+(hostname%2C+luna_group)+(node_load5)"
POWER_URL = "https://localhost:9090/api/v1/query?query=avg+by+(hostname%2C+luna_group)+(ipmi_dcmi_power_consumption_watts)"


def filter_columns(table=None):
    """
    This method remove the unnecessary fields from the dataset.
    """
    response = False
    static = {
        'rack': ['name', 'size', 'order', 'room', 'site'],
        'site': ['name', 'rooms'],
        'room': ['name', 'site', 'racks'],
        'inventory': ['name', 'type', 'height', 'orientation']
    }
    response = list(static[table])
    return response


def sortby(table=None):
    """
    This method remove the unnecessary fields from
    the dataset.
    """
    response = False
    static = {
        'bmcsetup': [
            'name', 'userid', 'username', 'password', 'netchannel', 'mgmtchannel',
            'unmanaged_bmc_users', 'comment'
        ]
    }
    response = list(static[table])
    return response
