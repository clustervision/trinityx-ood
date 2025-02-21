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
TRIX_CONFIG = '/trinity/local/etc/prometheus_server/rules/trix.rules'
ALERT_MANAGER_DIR = '/etc/trinity/passwords/prometheus'
APP_STATE = False  # False for Development, True for Production
