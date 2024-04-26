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
from flask import url_for
from datetime import datetime
import urllib.parse
from time import time
import base64
import binascii
import subprocess
from random import randrange, randint
from os import getpid
import hostlist
from nested_lookup import nested_lookup, nested_update, nested_delete, nested_alter
from nested_lookup import get_all_keys
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


    def prepare_payload(self, table=None, raw_data=None):
        """
        This method will prepare the payload.
        """
        payload = {k: v for k, v in raw_data.items() if v is not None}
        for key in EDITOR_KEYS:
            content = nested_lookup(key, payload)
            if content:
                if content[0] is True:
                    if table:
                        get_list = Rest().get_data(table, payload['name'])
                        if get_list:
                            value = nested_lookup(key, get_list)
                            if value:
                                content = self.open_editor(key, value[0], payload)
                                payload = nested_update(payload, key=key, value=content)
                    else:
                        content = self.open_editor(key, None, payload)
                        payload = nested_update(payload, key=key, value=content)
                elif content[0] is False:
                    payload = nested_delete(payload, key)
                elif content[0]:
                    if os.path.exists(content[0]):
                        if os.path.isfile(content[0]):
                            with open(content[0], 'rb') as file_data:
                                content = self.base64_encode(file_data.read())
                                payload = nested_update(payload, key=key, value=content)
                        else:
                            print(f'ERROR :: {content[0]} is a Invalid filepath.')
                    else:
                        content = self.base64_encode(bytes(content[0], 'utf-8'))
                        payload = nested_update(payload, key=key, value=content)
        return payload


    def open_editor(self, key=None, value=None, payload=None):
        """
        This Method will open a default text editor to
        write the multiline text for keys such as comment,
        prescript, postscript, partscript, content etc. but
        not limited to them only.
        """
        response = ''
        editor = str(os.path.abspath(__file__)).replace('helper.py', 'editor.sh')
        os.chmod(editor, 0o0755)
        random_path = str(time())+str(randint(1001,9999))+str(getpid())
        tmp_folder = f'/tmp/lunatmp-{random_path}'
        os.mkdir(tmp_folder)
        if key == 'content':
            filename = f'/tmp/lunatmp-{random_path}/{payload["name"]}{key}'
        else:
            filename = f'/tmp/lunatmp-{random_path}/{key}'
        temp_file = open(filename, "x", encoding='utf-8')
        if value:
            value = self.base64_decode(value)
            temp_file.write(value)
            temp_file.close()
        subprocess.call([editor, filename])
        with open(filename, 'rb') as file_data:
            response = self.base64_encode(file_data.read())
        os.remove(filename)
        os.rmdir(tmp_folder)
        return response



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
            pack_click = f'onclick="pack_osimage(\'{name}\');"'
            pack = f'<button type="button" {pack_click} class="{button}btn-secondary">Pack</button>'
            kernel = f'<a href="/kernel/{table}/{name}" class="{button}btn-dark">Change Kernel</a>'
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
            pack =  self.make_icon(
                href=None,
                onclick=f'pack_osimage(\'{name}\');',
                text=f'Pack {name}',
                icon='bx-package',
                color='#8592a3;'
            )
            kernel =  self.make_icon(
                href=url_for('kernel', record=name),
                onclick=None,
                text=f'Change Kernel Of {name}',
                icon='bx-microchip',
                color='#697a8d;'
            )
        else:
            info = ''
            edit = ''
            delete = ''
            clone = ''
            member = ''
            pack = ''
            kernel = ''
        action = {
            'osimage':  [info, edit, delete, clone, member, pack, kernel]
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


    def update_dict(self, data=None):
        """
        Deep Update the Dict
        """
        for key, value in data.items():
            if isinstance(value, str):
                value = None if value == 'None' else value
                if value is not  None:
                    data[key] = self.base64_decode(value)
                    return self.update_dict(data)
            else:
                return self.update_dict(data)
        return data


    def callback(self, value=None):
        """
        This method is a call back method for the nested lookup.
        """
        if isinstance(value, str):
            if value.lower() == 'none':
                value = None
            elif value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.lower() == 'null':
                value = None
        response = value
        if value not in  [None, True, False] and isinstance(value, str):
            response = self.base64_decode(value)
        return response


    def nested_dict(self, dictionary=None, limit=False):
        """
        This method will check the nested dictionary.
        """
        for key, value in dictionary.items():
            if isinstance(value, str):
                if key in EDITOR_KEYS:
                    doc = nested_alter({key : value}, key, self.callback)
                    dictionary[key] = self.less_content(doc[key], limit)
                else:
                    dictionary[key] = value
            elif isinstance(value, dict):
                return self.nested_dict(dictionary, limit)
            elif isinstance(value, list):
                return self.nested_list(dictionary, key, value, limit)
        return dictionary


    def nested_list(self, dictionary=None, key=None, value=None, limit=False):
        """
        This method will check the list for a dictionary.
        """
        response = []
        if value:
            for occurrence in value:
                if isinstance(occurrence, str):
                    if key in EDITOR_KEYS:
                        doc = nested_alter({key : occurrence}, key, self.callback)
                        response.append(self.less_content(doc[key], limit))
                    else:
                        response.append(occurrence)
                elif isinstance(occurrence, dict):
                    response.append(self.nested_dict(occurrence, limit))
        dictionary[key] = response
        return dictionary


    def less_content(self, content=None, limit=False):
        """
        This method will reduce the length of the content.
        """
        if limit:
            if content not in  [None, True, False] and isinstance(content, str):
                if len(content) > 60:
                    content = content[:60]+' ...'
        return content


    def prepare_json(self, json_data=None, limit=False):
        """
        This method will decode the base 64 string.
        """
        self.logger.debug(f'Data Limit => {limit}')
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(value, str):
                    if key in EDITOR_KEYS:
                        doc = nested_alter({key : value}, key, self.callback)
                        json_data[key] = self.less_content(doc[key], limit)
                    else:
                        json_data[key] = value
                elif isinstance(value, dict):
                    json_data[key] = self.nested_dict(value, limit)
                elif isinstance(value, list):
                    final_list = []
                    if value:
                        for occurrence in value:
                            if isinstance(occurrence, str):
                                doc = nested_alter({key : occurrence}, key, self.callback)
                                final_list.append(self.less_content(doc[key], limit))
                            elif isinstance(occurrence, dict):
                                final_list.append(self.nested_dict(occurrence, limit))
                    json_data[key] = final_list
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
