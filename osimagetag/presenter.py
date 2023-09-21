#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        if '\\n' in str(rows):
            self.table.align = "l"
        self.table.add_rows(rows)
        response = self.table.get_html_string(attributes={"id":"datatable", "class":table_class})
        return response


    def show_table_col(self, field=None, rows=None):
        """
        This method will fetch a records from
        the Luna 2 Daemon Database
        """
        self.logger.debug(f'Fields => {field}')
        self.logger.debug(f'Rows => {rows}')
        self.table.format = True
        self.table.add_column("Field", field)
        self.table.add_column("Values", rows)
        self.table.header = False
        self.table.align = "l"
        attribute = {}
        attribute['id'] = "my_table"
        attribute['class'] = "table table-bordered table-hover table-striped"
        response = self.table.get_html_string(attributes=attribute)
        return response


    def show_table_col_more_fields(self, field=None, newfield=None, rows=None):
        """
        This method will fetch a records from the Luna 2 Daemon Database
        """
        self.logger.debug(f'Fields => {field}')
        self.logger.debug(f'Rows => {rows}')
        self.table.add_column("Field", field)
        self.table.add_column("Field", newfield)
        self.table.add_column("Values", rows)
        self.table.header = False
        self.table.align = "l"
        attribute = {}
        attribute['id'] = "my_table"
        attribute['class'] = "table table-bordered table-hover table-striped"
        response = self.table.get_html_string(attributes=attribute)
        return response
