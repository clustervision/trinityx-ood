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
Helper Class for the AlertX.
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2025, TrinityX[AlertX]"
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
from random import randrange, randint
from os import getpid
from flask import url_for
import hostlist
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


    def get_color(self):
        """
        This method will generate HTML Hex color code randomly.
        """
        color = randrange(0, 2**24)
        hex_color = hex(color)
        response = "#" + hex_color[2:]
        return response


    def prepare_payload(self, table=None, raw_data=None):
        """
        This method will prepare the payload.
        """
        payload = {k: v for k, v in raw_data.items() if v is not None}
        for key in EDITOR_KEYS:
            content = nested_lookup(key, payload)
            if content:
                if content[0]:
                    content = self.base64_encode(bytes(content[0].replace('\r\n', '\n'), 'utf-8'))
                    payload = nested_update(payload, key=key, value=content)
        return payload


    def add_record(self, table=None, data=None):
        """
        This method will add a new record.
        """
        for remove in ['verbose', 'command', 'action']:
            data.pop(remove, None)
        payload = self.prepare_payload(None, data)
        request_data = {'config':{table:{payload['name']: payload}}}
        self.logger.debug(f'Payload => {request_data}')
        response = Rest().post_data(table, payload['name'], request_data)
        self.logger.debug(f'Response => {response}')
        return response


    def update_record(self, table=None, data=None):
        """
        This method will update a record.
        """
        for remove in ['verbose', 'command', 'action', 'hostname']:
            data.pop(remove, None)
        if 'raw' in data:
            data.pop('raw', None)
        payload = self.prepare_payload(table, data)
        name = None
        if 'name' in payload and 'cluster' not in table:
            name = payload['name']
            request_data = {'config':{table:{name: payload}}}
        else:
            request_data = {'config':{table: payload}}
        self.logger.debug(f'Payload => {request_data}')
        response = Rest().post_data(table, name, request_data)
        return response


    def clone_record(self, table=None, data=None):
        """
        This method will clone a record.
        """
        for remove in ['verbose', 'command', 'action']:
            data.pop(remove, None)
        payload = self.prepare_payload(table, data)
        request_data = {'config':{table:{payload['name']: payload}}}
        self.logger.debug(f'Payload => {request_data}')
        response = Rest().post_clone(table, payload['name'], request_data)
        self.logger.debug(f'Response => {response}')
        return response


    def collect_nodelist(self, nodelist=None):
        """
        This method provide the status of one or more nodes.
        """
        try:
            response = hostlist.collect_hostlist(nodelist)
        except hostlist.BadHostlist:
            response = "BadHostlist"
        return response


    def filter_data(self, table=None, data=None):
        """
        This method will generate the data as for
        row format
        """
        # self.logger.debug(f'Table => {table}')
        # self.logger.debug(f'Data => {data}')
        fields, rows, colored_fields = [], [], []
        fields = filter_columns(table)
        # self.logger.debug(f'Fields => {fields}')
        for field_key in fields:
            val_row = []
            for ele in data:
                if field_key in list((data[ele].keys())):
                    if isinstance(data[ele][field_key], list):
                        new_list = []
                        for internal in data[ele][field_key]:
                            if isinstance(internal, str):
                                new_list.append(internal)
                            else:
                                for internal_val in internal:
                                    # self.logger.debug(f'Key => {internal_val}')
                                    # self.logger.debug(f'Value => {internal[internal_val]}')
                                    in_key = internal_val
                                    in_val = internal[internal_val]
                                    new_list.append(f'{in_key} = {in_val} ')
                        new_list = '\n'.join(new_list)
                        val_row.append(new_list)
                        new_list = []
                    elif field_key == 'tpm_uuid':
                        if data[ele][field_key]:
                            val_row.append(True)
                        else:
                            val_row.append(False)
                    else:
                        if data[ele][field_key] in [True, False, None, '', 'None']:
                            value = self.format_value(data[ele][field_key])
                            val_row.append(value)
                        else:
                            val_row.append(data[ele][field_key])
                else:
                    val_row.append(self.format_value(None))
            rows.append(val_row)
            # self.logger.debug(f'Each Row => {val_row}')
            val_row = []
            colored_fields.append(field_key)
        fields = colored_fields
        final_rows = []
        for array in range(len(rows[0])):
            tmp = []
            for element in rows:
                tmp.append(element[array])
            final_rows.append(tmp)
        rows = final_rows
        for row in rows:
            action = self.action_items(table, row[0])
            row.insert(len(row), action)
        # Adding Serial Numbers to the dataset
        fields.insert(0, 'S. No.')
        fields.insert(len(fields),"Actions")
        num = 1
        for outer in rows:
            outer.insert(0, num)
            num = num + 1
        # Adding Serial Numbers to the dataset
        return fields, rows


    def make_icon(self, href=None, onclick=None, text=None, icon=None, color=None):
        """
        This method will create action item on-demand.
        """
        if href:
            href = f'href="{href}"'
        else:
            href = ''
        if onclick:
            onclick = f'onclick="{onclick}"'
        else:
            onclick = ''
        data = 'id="actions" '
        data += 'data-bs-toggle="tooltip" '
        data += 'data-bs-offset="0,4" '
        data += 'data-bs-placement="top" '
        data += 'data-bs-html="true" '
        inner = f'<i class=\'bx bxs-arrow-from-left bx-xs\'></i> <span>{text}</span>'
        data += f'data-bs-original-title="{inner}" '
        icon = f'<i class="bx bx-md {icon}" style="color: {color}"></i>'
        item = f'<a {href} {onclick} {data}>{icon}</a>'
        return item


    def action_items(self, table=None, name=None):
        """
        This method provide the action items for the table. 
        """
        ## Here we have two strategy to show action items. One with buttons and one with icons.
        ## I choose icons here with tooltips. If in future buttons are required instead of icons
        ## than set the value of items to button
        item_type = 'icon'
        if item_type == 'button':
            button = "btn btn-sm "
            info = f'<a href="/show/{name}" class="{button}btn-info">Info</a>'
            edit = f'<a href="/edit/{name}" class="{button}btn-primary">Edit</a>'
            delete = f'<a href="/delete/{name}" class="{button}btn-danger">Delete</a>'
            clone = f'<a href="/clone/{name}" class="{button}btn-warning">Clone</a>'
            member_click = f'onclick="member(\'osimage\', \'{name}\');"'
            member_button = f'class="{button}rounded-pill btn-outline-primary"'
            member = f'<button type="button" {member_click} {member_button}>Member Nodes</button>'
        elif item_type == 'icon':
            info =  self.make_icon(
                href=url_for('show', record=name),
                onclick=None,
                text=f'{name} Detail Information',
                icon='bx-info-circle',
                color='#03c3ec;'
            )
            edit =  self.make_icon(
                href=url_for('edit', record=name),
                onclick=None,
                text=f'Change in {name}',
                icon='bx-edit',
                color='#696cff;'
            )
            delete =  self.make_icon(
                href=url_for('delete', record=name),
                onclick=f'return confirm(\'Are you sure you want to delete {name}?\');',
                text=f'Delete {name}',
                icon='bx-trash',
                color='red;'
            )
            clone =  self.make_icon(
                href=url_for('clone', record=name),
                onclick=None,
                text=f'Clone {name}',
                icon='bx-duplicate',
                color='#20c997;'
            )
            member =  self.make_icon(
                href=None,
                onclick=f'member(\'{table}\', \'{name}\');',
                text=f'Member Nodes of {name}',
                icon='bx-copy-alt',
                color='#007bff;'
            )
        else:
            info = ''
            edit = ''
            delete = ''
            clone = ''
            member = ''
        action = {
            'bmcsetup': [info, edit, delete, clone, member]
        }
        response = "&nbsp;".join(action[table])
        return response


    def format_value(self, value=None):
        """
        This method will format true, false, and none in html format.
        """
        if value is True:
            value = '<span class="badge bg-label-success me-1">True</span>'
        elif value is False:
            value = '<span class="badge bg-label-warning me-1">False</span>'
        # elif value is None or value == '' or 'None' in value:
        elif value in [None, '', 'None']:
            value = '<span class="badge bg-label-dark me-1">None</span>'
        return value


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


    def filter_data_col(self, table=None, data=None):
        """
        This method will generate the data as for
        row format
        """
        self.logger.debug(f'Table => {table} and Data => {data}')
        defined_keys = sortby(table)
        self.logger.debug(f'Fields => {defined_keys}')
        for new_key in list(data.keys()):
            if new_key not in defined_keys:
                defined_keys.append(new_key)
        index_map = {v: i for i, v in enumerate(defined_keys)}
        data = sorted(data.items(), key=lambda pair: index_map[pair[0]])
        self.logger.debug(f'Sorted Data => {data}')
        fields, rows = [], []
        for key in data:
            fields.append(f"<strong>{key[0].capitalize()}</strong>")
            if isinstance(key[1], list):
                new_list = []
                for internal in key[1]:
                    for internal_val in internal:
                        self.logger.debug(f'Key: {internal_val} Value: {internal[internal_val]}')
                        if internal[internal_val] in [True, False, None]:
                            internal[internal_val] = self.format_value(internal[internal_val])
                        if internal_val == "interface":
                            new_list.append(f'{internal_val} = {internal[internal_val]}')
                        else:
                            new_list.append(f'  {internal_val} = {internal[internal_val]}')
                new_list = '\n'.join(new_list)
                rows.append(new_list)
                new_list = []
            elif isinstance(key[1], dict):
                new_list = []
                for internal in key[1]:
                    self.logger.debug(f'Key => {internal} and Value => {key[1][internal]}')
                    in_key = internal
                    in_val = key[1][internal]
                    if in_val in [True, False, None]:
                        value = self.format_value(in_val)
                        new_list.append(f'{in_key} = {value} ')
                    else:
                        new_list.append(f'{in_key} = {in_val} ')
                new_list = '\n'.join(new_list)
                rows.append(new_list)
                new_list = []
            else:
                if key[1] in [True, False, None]:
                    value = self.format_value(key[1])
                    rows.append(value)
                else:
                    rows.append(key[1])
        return fields, rows
