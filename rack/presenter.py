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
Presenter Class for the WEB
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2022, Luna2 Project [WEB]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Development"

from prettytable import PrettyTable
from log import Log


class Presenter():
    """
    All kind of display methods.
    """

    def __init__(self):
        """
        Constructor - As of now, nothing have to initialize.
        """
        self.logger = Log.get_logger()
        self.table = PrettyTable()


    def show_table(self, fields=None, rows=None, dark=None):
        """
        This method will fetch a records from
        the Luna 2 Daemon Database
        """
        table_class = 'datatable table table-bordered table-hover table-striped'
        if dark:
            table_class = f'{table_class} table-dark'
        self.logger.debug(f'Fields => {fields}')
        self.logger.debug(f'Rows => {rows}')
        self.table.format = True
        self.table.field_names = fields
        # self.table.align = "l"
        self.table.add_rows(rows)
        response = self.table.get_html_string(attributes={"id":"datatable", "class":table_class})
        return response
