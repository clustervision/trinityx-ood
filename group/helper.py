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


    def filter_interfaces(self, request=None, table=None, payload=None):
        """
        This method
        """
        interface = request.form.getlist('interface')
        ipaddress = request.form.getlist('ipaddress')
        macaddress = request.form.getlist('macaddress')
        network = request.form.getlist('network')
        options = request.form.getlist('options')
        vlanid = request.form.getlist('vlanid')

        vlan_parent = request.form.getlist('vlan_parent')
        bond_mode = request.form.getlist('bond_mode')
        bond_slaves = request.form.getlist('bond_slaves')

        dhcp = request.form.getlist('dhcp')
        interface_list = []
        if table == 'node':
            zip_interface = zip(interface, ipaddress, macaddress, network, options, vlan_parent, bond_mode, bond_slaves)
            for interface, ipaddress, macaddress, network, options, vlan_parent, bond_mode, bond_slaves in zip_interface:
                tmp_interface = {}
                if interface:
                    tmp_interface['interface'] = interface
                if ipaddress:
                    tmp_interface['ipaddress'] = ipaddress
                if macaddress:
                    tmp_interface['macaddress'] = macaddress
                if network:
                    tmp_interface['network'] = network
                if options:
                    tmp_interface['options'] = options
                
                if vlan_parent:
                    tmp_interface['vlan_parent'] = vlan_parent
                if bond_mode:
                    tmp_interface['bond_mode'] = bond_mode
                if bond_slaves:
                    tmp_interface['bond_slaves'] = bond_slaves
                
                interface_list.append(tmp_interface)
        elif table =='group':
            zip_interface = zip(interface, network, options, vlanid, dhcp, vlan_parent, bond_mode, bond_slaves)
            for interface, network, options, vlanid, dhcp, vlan_parent, bond_mode, bond_slaves in zip_interface:
                tmp_interface = {}
                if interface:
                    tmp_interface['interface'] = interface
                if network:
                    tmp_interface['network'] = network
                if vlanid and len(vlanid) > 0 and vlanid.strip():
                    tmp_interface['vlanid'] = vlanid
                if dhcp:
                    tmp_interface['dhcp'] = True if dhcp.lower() == 'true' else False
                if options:
                    tmp_interface['options'] = options
                if vlan_parent:
                    tmp_interface['vlan_parent'] = vlan_parent
                if bond_mode:
                    tmp_interface['bond_mode'] = bond_mode
                if bond_slaves:
                    tmp_interface['bond_slaves'] = bond_slaves
                interface_list.append(tmp_interface)
        if 'interface' in payload:
            del payload['interface']
        if 'ipaddress' in payload:
            del payload['ipaddress']
        if 'macaddress' in payload:
            del payload['macaddress']
        if 'network' in payload:
            del payload['network']
        if 'options' in payload:
            del payload['options']
        if 'vlanid' in payload:
            del payload['vlanid']
        if 'dhcp' in payload:
            del payload['dhcp']
        if 'vlan_parent' in payload:
            del payload['vlan_parent']
        if 'bond_mode' in payload:
            del payload['bond_mode']
        if 'bond_slaves' in payload:
            del payload['bond_slaves']
        payload['interfaces'] = interface_list
        return payload


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
        datacopy=data.copy()
        for ele in datacopy.keys():
            if '_override' in datacopy[ele]:
                if datacopy[ele]['_override'] and 'name' in datacopy[ele]:
                    data[ele]['name'] = f"{data[ele]['name']} *"
                del data[ele]['_override']
                if '_override' in fields:
                    fields.remove('_override')

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
        if '*' in name:
            name = name.replace(" ", "")
            name = name.replace("*", "")
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
            ospush = f'<a href="/ospush/{table}/{name}" class="{button}btn-dark">OS Push</a>'
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
            ospush =  self.make_icon(
                href=url_for('ospush', record=name),
                onclick=None,
                text=f'Push OS for {name}',
                icon='bxs-package',
                color='#697a8d;'
            )
        else:
            info = ''
            edit = ''
            delete = ''
            clone = ''
            member = ''
            ospush = ''
        action = {
            'group':    [info, edit, delete, clone, member, ospush]
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


    def filter_data_col(self, table=None, data=None):
        """
        This method will generate the data as for
        row format
        """
        self.logger.debug(f'Table => {table} and Data => {data}')
        defined_keys = sortby(table)
        self.logger.debug(f'Fields => {defined_keys}')
        merge_exception = None
        data, override = self.merge_source(table, data, merge_exception)
        datacopy = data.copy()
        for key in datacopy.keys():
            if key == '_override':
                if data[key]:
                    data['info'] = "Config differs from parent - local overrides"
                del data[key]
        for new_key in list(data.keys()):
            if new_key not in defined_keys:
                defined_keys.append(new_key)
        index_map = {v: i for i, v in enumerate(defined_keys)}
        data = sorted(data.items(), key=lambda pair: index_map[pair[0]])
        self.logger.debug(f'Sorted Data => {data}')
        fields, rows = [], []
        for key in data:
            key_name = key[0]
            if key_name in override:
                key_name += ' *'
            fields.append(key_name)
            if isinstance(key[1], list):
                interface_html = ""
                for internal in key[1]:
                    interface_html += '<pre style="border: 1px solid #000; color: #000; background-color: #f2f1e1; font-size: 14px;">'
                    for internal_val in internal:
                        self.logger.debug(f'Key: {internal_val} Value: {internal[internal_val]}')
                        if internal[internal_val] in [True, False, None]:
                            internal[internal_val] = self.format_value(internal[internal_val])
                        if internal_val == "interface":
                            interface_html += f'{internal_val} = {internal[internal_val]}<br />'
                        else:
                            interface_html += f'&nbsp;&nbsp;&nbsp;{internal_val} = {internal[internal_val]}<br />'
                    interface_html += '</pre><br />'
                interface_html = interface_html[:-6]
                rows.append(interface_html)
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
                    if key[0] == '_override':
                        rows.append(key[1])
                    else:
                        value = self.format_value(key[1])
                        rows.append(value)
                else:
                    rows.append(key[1])
        return fields, rows


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

