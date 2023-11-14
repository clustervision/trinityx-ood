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

from log import Log
from constant import filter_columns


class Helper():
    """
    All kind of helper methods.
    """

    def __init__(self):
        """
        Constructor - As of now, nothing have to initialize.
        """
        self.logger = Log.get_logger()


    def filter_interface(self, table=None, data=None):
        """
        This method will generate the data as for
        row format from the interface
        """
        self.logger.debug(f'table => {table}')
        self.logger.debug(f'data => {data}')
        fields, rows, colored_fields = [], [], []
        fields = filter_columns(table)
        self.logger.debug(f'fields => {fields}')
        for field_key in fields:
            val_row = []
            for ele in data:
                if field_key in list(ele.keys()):
                    if ele[field_key] == 'in progress':
                        text = '<strong style="color: green;">In Progress</strong>'
                        val_row.append(text)
                    elif ele[field_key] == 'queued':
                        text = '<strong style="color: orange;">Queued</strong>'
                        val_row.append(text)
                    elif ele[field_key] == 1:
                        text = '<strong style="color: green;">yes</strong>'
                        val_row.append(text)
                    elif ele[field_key] == 0:
                        text = '<strong style="color: orange;">no</strong>'
                        val_row.append(text)
                    elif ele[field_key] == 'maintask':
                        text = '<strong style="color: blue;">Main Task</strong>'
                        val_row.append(text)
                    elif ele[field_key] == 'subtask':
                        text = '<strong style="color: magenta;">Sub Task</strong>'
                        val_row.append(text)
                    else:
                        val_row.append(ele[field_key])
                else:
                    val_row.append("--NA--")
                self.logger.debug(f'Element => {ele}')
            rows.append(val_row)
            val_row = []
            colored_fields.append(field_key)
        fields = colored_fields
        self.logger.debug(f'Rows before Swapping => {rows}')
        final_rows = []
        for array in range(len(rows[0])) :
            tmp = []
            for element in rows:
                tmp.append(element[array])
            final_rows.append(tmp)
        rows = final_rows
        # Adding Serial Numbers to the dataset
        fields.insert(0, '#')
        num = 1
        for outer in rows:
            outer.insert(0, num)
            num = num + 1
        # Adding Serial Numbers to the dataset
        return fields, rows
