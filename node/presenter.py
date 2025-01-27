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

import json
from prettytable import PrettyTable
from bs4 import BeautifulSoup
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


    def show_json(self, json_data=None):
        """
        This method will fetch all records from
        the Luna 2 Daemon Database
        """
        self.logger.debug(f'Jason Data => {json_data}')
        pretty = json.dumps(json_data, indent=2)
        return pretty


    def add_class_to_tr_if_second_td_contains_star(self, html_table):
        """
        This method will find the * and apply a color on the tr.
        """
        soup = BeautifulSoup(html_table, 'html.parser')
        for tr in soup.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) > 1 and '*' in tds[1].get_text():
                tr['class'] = tr.get('class', []) + ['table-success']
        return str(soup)


    def add_class_to_tr_if_script_is_not_default(self, html_table):
        """
        This method will find the * and apply a color on the tr.
        """
        soup = BeautifulSoup(html_table, 'html.parser')
        for i, tr in enumerate(rows):
        tds = tr.find_all('td')
        if len(tds) > 1:
            key = tds[0].get_text().strip()
            value = tds[1].get_text().strip()

            # Check if key has '_source' and value is 'node'
            if '_source' in key and value == 'node':
                tr['class'] = tr.get('class', []) + ['table-success']
                tr['class'] = tr.get('class', []) + ['table-success']
        return str(soup)


    def show_table(self, fields=None, rows=None, dark=None):
        """
        This method will fetch a records from
        the Luna 2 Daemon Database class="table-success"
        """
        table_class = 'datatable table table-bordered table-hover table-striped'
        if dark:
            table_class = f'{table_class} table-dark'
        self.logger.debug(f'Fields => {fields}')
        self.logger.debug(f'Rows => {rows}')
        self.table.format = True
        self.table.field_names = fields
        if '\\n' in str(rows):
            self.table.align = "l"
        for row in rows:
            self.table.add_row(row)
        response = self.table.get_html_string(attributes={"id":"datatable", "class":table_class})
        modified_html = self.add_class_to_tr_if_second_td_contains_star(response)
        return modified_html


    def show_table_col(self, field=None, rows=None):
        """
        This method will fetch a records from
        the Luna 2 Daemon Database
        """
        self.logger.debug(f'Fields => {field}')
        self.logger.debug(f'Rows => {rows}')
        self.table.format = True
        for key, value in zip(field, rows):
            # if "script" in key:
                # self.table.add_row([key, value])
                # if key in ["partscript_source", "postscript_source", "prescript_source"] and value == "node":

                # else:
                #     self.table.add_row([key, value], divider=True)
                # self.table.add_row(["", ""])
            # else:
                if key != '_override':
                    self.table.add_row([key, value])
        self.table.align = "l"
        attribute = {}
        attribute['id'] = "my_table"
        attribute['class'] = "table table-bordered table-hover table-striped"
        # response = self.table.get_html_string(attributes=attribute)
        # return response
        response = self.table.get_html_string(attributes=attribute)
        modified_html = self.add_class_to_tr_if_script_is_not_default(response)
        return modified_html
