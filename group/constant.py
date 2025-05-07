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
APP_STATE = True # False for Development, True for Production


def overrides(table=None):
    """
    This method has information regarding what could be an override for what table: node, group, cluster, etc
    """
    response = False
    static = {
        'group': [
            'provision_method', 'provision_interface', 'provision_fallback', 'kerneloptions', 'osimagetag'
        ]
    }
    if table and table in static:
        response = list(static[table])
    return response



def filter_columns(table=None):
    """
    This method remove the unnecessary fields from
    the dataset.
    """
    response = False
    static = {
        'group': ['name', 'bmcsetupname', 'osimage', 'osimagetag', 'roles', 'interfaces'],
        'groupinterface': ['interface', 'network', 'options', 'vlanid', 'vlan_parent', 'bond_mode', 'bond_slaves', 'dhcp'],
        'groupsecrets': ['Group', 'name', 'path', 'content']
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
        'group': [
            'info', 'name', 'domain', 'osimage', 'osimagetag', 'kerneloptions', 'interfaces', 'setupbmc',
            'bmcsetupname', 'unmanaged_bmc_users', 'netboot', 'bootmenu', 'roles', 'scripts_source',
            'scripts', 'prescript_source', 'prescript', 'partscript_source', 'partscript',
            'postscript_source', 'postscript', 'provision_interface', 'provision_method',
            'provision_fallback', 'comment'
        ],
        'groupinterface': ['interfacename', 'network'],
        'groupsecrets': ['Group', 'name', 'path', 'content']
    }
    response = list(static[table])
    return response
