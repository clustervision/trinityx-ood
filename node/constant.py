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


def filter_columns(table=None):
    """
    This method remove the unnecessary fields from
    the dataset.
    """
    response = False
    static = {
        'node': ['name', 'group', 'osimage', 'osimagetag', 'setupbmc', 'bmcsetup', 'status', 'tpm_uuid'],
        'nodeinterface': ['interface', 'ipaddress', 'macaddress', 'network', 'options'],
        'nodesecrets': ['Node', 'name', 'path', 'content']
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
        'node': [
            'name', 'hostname', 'group', 'osimage', 'osimagetag', 'kerneloptions', 'interfaces',
            'status', 'vendor', 'assettag', 'position', 'switch', 'switchport', 'cloud', 'setupbmc',
            'bmcsetup', 'unmanaged_bmc_users', 'netboot', 'bootmenu', 'service', 'roles', 'scripts',
            'prescript', 'partscript', 'postscript','provision_interface', 'provision_method',
            'provision_fallback', 'tpm_uuid', 'tpm_pubkey', 'tpm_sha256', 'comment',  'macaddress'
        ],
        'nodeinterface': ['interface', 'ipaddress', 'macaddress', 'network'],
        'nodesecrets': ['Node', 'name', 'path', 'content']
    }
    response = list(static[table])
    return response
