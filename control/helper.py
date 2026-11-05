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
Helper Class for the Luna WEB
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2022, Luna2 Project [WEB]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Development"

import hostlist
from log import Log
from rest import Rest

class Helper():
    """
    All kind of helper methods.
    """

    def __init__(self):
        """
        Constructor - As of now, nothing have to initialize.
        """
        self.logger = Log.get_logger()


    def collect_nodelist(self, nodelist=None):
        """
        This method provide the status of one or more nodes.
        """
        try:
            response = hostlist.collect_hostlist(nodelist)
        except hostlist.BadHostlist:
            response = "BadHostlist"
        return response


    def get_name_list(self, table=None):
        """
        This method will open the Login Page(First Page)
        """
        response = []
        get_list = Rest().get_data(table)
        if get_list:
            raw_data = get_list['config'][table]
            response = list(raw_data.keys())
        return response

    @staticmethod
    def is_setupbmc_enabled(value):
        """
        Match node app semantics: empty / inherit → default True; only explicit false disables BMC.
        """
        if value is False:
            return False
        if isinstance(value, str) and value.strip().lower() in ('false', 'no', '0'):
            return False
        return True

    def get_node_setupbmc_map(self):
        """
        Return {node_name: bool} for setupbmc from Luna node config.
        Missing nodes default to True (BMC assumed available).
        """
        out = {}
        get_list = Rest().get_data('node')
        if not get_list:
            return out
        raw = (get_list.get('config') or {}).get('node') or {}
        if not isinstance(raw, dict):
            return out
        for name, rec in raw.items():
            key = str(name).strip()
            if not key:
                continue
            value = None
            if isinstance(rec, dict):
                value = rec.get('setupbmc')
            out[key] = self.is_setupbmc_enabled(value)
        return out

    def filter_sel_hostlist(self, node_list):
        """
        Keep only nodes with setupbmc enabled. Returns (enabled_names, skipped_names).
        """
        if not node_list:
            return [], []
        setupbmc_map = self.get_node_setupbmc_map()
        enabled = []
        skipped = []
        for name in node_list:
            node = str(name).strip()
            if not node:
                continue
            # Default True when node is not in the map (same as node form DEFAULT).
            if setupbmc_map.get(node, True):
                enabled.append(node)
            else:
                skipped.append(node)
        return enabled, skipped
