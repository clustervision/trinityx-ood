#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This code is part of the TrinityX software suite
# Copyright (C) 2026  ClusterVision Solutions b.v.
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
__copyright__   = "Copyright 2026, Luna2 Project [OOD]"
__license__     = "GPL"
__version__     = "3.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Production"


from rest import Rest
from log import Log

class Model():
    """
    All kind of Models methods.
    """

    def __init__(self):
        """
        Constructor - As of now, nothing have to initialize.
        """
        self.logger = Log.get_logger()


    def get_list_options_json(self, table:str, selected=None):
        """
        Plain option names for Vue selects: { "options": [...], "selected": ... }.
        """
        names = []
        get_list = Rest().get_data(table)
        if "status" in get_list:
            if get_list["status"] is True:
                raw_data = get_list['content']['config'][table]
                names = list(raw_data.keys())
            else:
                names = [get_list['content']['message']]
        else:
            names = ["Nothing Available"]
        return {"options": names, "selected": selected}
