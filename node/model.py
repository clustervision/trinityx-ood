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
Main Model Class for the Luna WEB
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2022, Luna2 Project [WEB]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Development"


from rest import Rest
from log import Log

class Model():
    """
    All kind of helper methods.
    """

    def __init__(self):
        """
        Constructor - As of now, nothing have to initialize.
        """
        self.logger = Log.get_logger()


    def get_list_option_html(self, table=None, record=None, source=None):
        """
        This method will open the Login Page(First Page)
        """
        response = ""
        get_list = Rest().get_data(table)
        if get_list:
            raw_data = get_list['config'][table]
            response += f"<option value=''> Select {table.capitalize()}  </option>"
            for name, _ in raw_data.items():
                if record:
                    if record == name:
                        if source:
                            if source == 'node':
                                response += f"<option value='{name}(group)'>{name} (group)</option>"
                                response += f"<option value='{name}(node)' selected>{name} (node)</option>"
                            else:
                                response += f"<option value='{name}(group)' selected>{name} (group)</option>"
                                response += f"<option value='{name}(node)'>{name} (node)</option>"
                        else:
                            response += f"<option value='{name}' selected>{name}</option>"
                    else:
                        response += f"<option value='{name}'>{name}</option>"
                else:
                    response += f"<option value='{name}'>{name}</option>"
        else:
            response += f"<option value=''>No {table.capitalize()} Available </option>"
        return response


    def get_list_options(self, table=None):
        """
        This method will open the Login Page(First Page)
        """
        response = []
        get_list = Rest().get_data(table)
        if get_list:
            raw_data = get_list['config'][table]
            response = [["", f" Select {table.capitalize()}  "]]
            for name, _ in raw_data.items():
                name_list = [name, name]
                response = response + [name_list]
        else:
            response = [["", f" No {table.capitalize()} Available  "]]
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


    def get_record(self, table=None, record=None):
        """
        This method will open the Login Page(First Page)
        """
        response = []
        get_list = Rest().get_data(table, record)
        if get_list:
            raw_data = get_list['config'][table][record]
            response = raw_data
        return response


    def get_count(self, table=None):
        """
        This method will open the Login Page(First Page)
        """
        response = 0
        get_list = Rest().get_data(table)
        if get_list:
            response = len(get_list['config'][table])
        return response
