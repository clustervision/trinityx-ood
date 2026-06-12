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

import os
from time import time
import base64
import binascii
import subprocess
from random import randint
from os import getpid
from flask import url_for
from nested_lookup import nested_lookup, nested_update, nested_delete
from rest import Rest
from log import Log
from constant import filter_columns, EDITOR_KEYS, sortby


class Helper():
    """
    All kind of helper methods.
    """

    def __init__(self):
        """
        Constructor - As of now, nothing have to initialize.
        """
        self.logger = Log.get_logger()


    def base64_encode(self, content=None):
        """
        This method will encode a base 64 string.
        """
        try:
            if content is not None:
                content = base64.b64encode(content).decode("utf-8")
        except binascii.Error:
            self.logger.debug(f'Base64 Encode Error => {content}')
        return content


    def base64_decode(self, content=None):
        """
        This method will decode the base 64 string.
        """
        try:
            if content is not None:
                content = base64.b64decode(content)
                content = content.decode("utf-8")
        except binascii.Error:
            self.logger.debug(f'Base64 Decode Error => {content}')
        except UnicodeDecodeError:
            self.logger.debug(f'Base64 Unicode Decode Error => {content}')
        return content


    def prepare_json(self, json_data=None, limit=False):
        """
        This method will decode the base 64 string.
        """
        for key in EDITOR_KEYS:
            content = nested_lookup(key, json_data)
            if content:
                if content[0] is not None:
                    try:
                        content = self.base64_decode(content[0])
                        if limit:
                            if len(content) and '<empty>' not in content:
                                content = content[:60]
                                if '\n' in content:
                                    content = content.removesuffix('\n')
                                content = f'{content}...'
                        json_data = nested_update(json_data, key=key, value=content)
                    except TypeError:
                        self.logger.debug(f"Without any reason {content} is coming from api.")
        return json_data


    def get_secrets(self, table=None, data=None):
        """
        This method will filter data for Secrets
        """
        self.logger.debug(f'Table => {table} and Data => {data}')
        rows, colored_fields = [], []
        fields = filter_columns(table)
        self.logger.debug(f'Fields => {fields}')
        for key in data:
            new_row = []
            for value in data[key]:
                self.logger.debug(f'Key => {key} and Value => {value}')
                new_row.append(key)
                new_row.append(value['name'])
                new_row.append(value['path'])
                content = self.base64_decode(value['content'])
                new_row.append(content[:60]+'...')
                rows.append(new_row)
                new_row = []
        for newfield in fields:
            colored_fields.append(newfield)
        fields = colored_fields
        for outer in rows:
            action = self.action_items(table, f'{outer[0]}/{outer[1]}')
            outer.insert(len(outer), action)
        # Adding Serial Numbers to the dataset
        fields.insert(0, 'S. No.')
        fields.insert(len(fields),"Actions")
        num = 1
        for outer in rows:
            outer.insert(0, num)
            num = num + 1
        # Adding Serial Numbers to the dataset
        return fields, rows


    def filter_secret_col(self, table=None, data=None):
        """
        This method will generate the data as for row format
        """
        self.logger.debug(f'Table => {table} and Data => {data}')
        rows, colored_fields = [], []
        fields = sortby(table)
        self.logger.debug(f'Fields => {fields}')
        for key in data:
            new_row = []
            for value in data[key]:
                self.logger.debug(f'Key => {key} and Value => {value}')
                new_row.append(key)
                new_row.append(value['name'])
                new_row.append(value['path'])
                content = self.base64_decode(value['content'])
                new_row.append(content)
                rows.append(new_row)
                new_row = []
        for newfield in fields:
            colored_fields.append(newfield)
        fields = colored_fields
        new_fields, new_row = [], []
        for row in rows:
            new_fields = new_fields + fields
            new_row = new_row + row
        return new_fields, new_row
