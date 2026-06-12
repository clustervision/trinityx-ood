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

import base64
import binascii
from copy import deepcopy
import hostlist
from flask import url_for
from nested_lookup import nested_lookup, nested_update, nested_alter
from rest import Rest
from log import Log
from constant import filter_columns, EDITOR_KEYS, sortby, overrides


class Helper():
    """
    All kind of helper methods.
    """

    def __init__(self):
        """
        Constructor - As of now, nothing have to initialize.
        """
        self.logger = Log.get_logger()


    def app_url(self, request=None):
        """
        URL for the frontend application (window.APP_URL).
        """
        response = {"APP_URL": ""}
        full_url = f"{request.scheme}://{request.host}{request.path}"
        full_url = full_url[:-1]
        full_url_app = f"{full_url}{url_for('home')}"
        APP_URL = full_url_app[:-1]
        response["APP_URL"] = APP_URL
        return response


    def get_bond_mode_options(self, bond_mode=None):
        """
        This method will return the bond mode options in HTML format.
        """
        mode_list = [
            "<option value=''>--- Select Bond Mode ---</option>",
            "<option value='balance-rr'>balance-rr</option>",
            "<option value='active-backup'>active-backup</option>",
            "<option value='balance-xor'>balance-xor</option>",
            "<option value='broadcast'>broadcast</option>",
            "<option value='802.3ad'>802.3ad</option>",
            "<option value='balance-tlb'>balance-tlb</option>",
            "<option value='balance-alb'>balance-alb</option>",
        ]
        if bond_mode:
            for i, mode in enumerate(mode_list):
                if f"value='{bond_mode}'" in mode:
                    mode_list[i] = f"<option value='{bond_mode}' selected>{bond_mode}</option>"
                    break
        response = "".join(mode_list)
        return response


    def prepare_payload(self, raw_data=None):
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
        payload = self.prepare_payload(data)
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
        payload = self.prepare_payload(data)
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
        payload = self.prepare_payload(data)
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
        if isinstance(json_data, list):
            new_json_data=[]
            for list_data in json_data:
                new_json_data.append(self.prepare_json(list_data, limit))
            return new_json_data
        elif isinstance(json_data, dict):
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


    def merge_source(self, table=None, data=None, exception=None):
        """
        This method will merge *_source field to the real field with braces and remove the
        *_source keys from the output.
        """
        exception = []
        response = deepcopy(data)
        override = overrides(table)
        resp_overrides = []
        for key, value in data.items():
            script = True if 'part' in key or 'post' in key or 'pre' in key else False
            if '_source' in key:
                raw_name = key.replace('_source', '')
                if raw_name.startswith('_'):
                    raw_name = raw_name[1:]
                if table == value:
                    if raw_name in override:
                        resp_overrides.append(raw_name)
                if exception and raw_name in exception:
                    default_value = data[key]
                    response[key] = f'({default_value})'
                    default_value = data[raw_name].rstrip()
                    if len(default_value) == 0:
                        response[raw_name] = '<empty>'
                    else:
                        response[raw_name] = default_value
                    continue
                if isinstance(data[raw_name], str):
                    default_value = data[raw_name].rstrip()
                    if len(default_value) == 0:
                        default_value = '<empty>'
                else:
                    default_value = data[raw_name]
                if value in data:
                    if script is True and default_value != '<empty>':
                        response[raw_name] = f'({data[value]}) {default_value}'
                    else:
                        response[raw_name] = f'{default_value} ({data[value]})'
                else:
                    if str(value) == str(table):
                        response[raw_name] = f'{default_value}'
                    else:
                        if script is True and default_value != '<empty>':
                            response[raw_name] = f'({value}) {default_value}'
                        else:
                            response[raw_name] = f'{default_value} ({value})'
                del response[key]
        return response, resp_overrides


    def get_bond_mode_list(self):
        """
        Bond mode options as a plain list (no HTML), for JSON add/edit/clone bodies.
        """
        return [
            'balance-rr', 'active-backup', 'balance-xor',
            'broadcast', '802.3ad', 'balance-tlb', 'balance-alb',
        ]

