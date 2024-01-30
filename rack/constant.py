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

from flask import url_for

INI_FILE = '/trinity/local/ondemand/3.0/config/luna.ini'
LICENSE = '/trinity/local/ondemand/3.0/LICENSE.txt'
LOG_DIR = '/var/log/luna'
LOG_FILE = '/var/log/luna/luna2-web.log'
EDITOR_KEYS = ['options', 'content', 'comment', 'prescript', 'partscript', 'postscript']

# RACK_CLASS = {
#    "default": url_for('static', filename='img/supermicro-1.png'),
#    "noname": url_for('static', filename='img/noname.png'),
#    "switch": url_for('static', filename='img/switch.png'),

#    "asus-1": url_for('static', filename='img/asus-1.png'),
#    "asus-2": url_for('static', filename='img/asus-2.png'),
#    "asus-3": url_for('static', filename='img/asus-3.png'),
#    "asus-4": url_for('static', filename='img/asus-4.png'),

#    "dell-1": url_for('static', filename='img/dell-1.png'),
#    "dell-2": url_for('static', filename='img/dell-2.png'),
#    "dell-4": url_for('static', filename='img/dell-4.png'),

#    "gigabyte-1": url_for('static', filename='img/gigabyte-1.png'),
#    "gigabyte-2": url_for('static', filename='img/gigabyte-2.png'),
#    "gigabyte-4": url_for('static', filename='img/gigabyte-4.png'),

#    "hp-1": url_for('static', filename='img/hp-1.png'),
#    "hp-2": url_for('static', filename='img/hp-2.png'),
#    "hp-4": url_for('static', filename='img/hp-4.png'),

#    "lenovo-1": url_for('static', filename='img/lenovo-1.png'),
#    "lenovo-2": url_for('static', filename='img/lenovo-2.png'),
#    "lenovo-3": url_for('static', filename='img/lenovo-3.png'),

#    "supermicro-1": url_for('static', filename='img/supermicro-1.png'),
#    "supermicro-2": url_for('static', filename='img/supermicro-2.png'),
#    "supermicro-3": url_for('static', filename='img/supermicro-3.png'),
#    "supermicro-4": url_for('static', filename='img/supermicro-4.png')


# }



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
