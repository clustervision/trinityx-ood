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
import requests
from flask import url_for
from nested_lookup import nested_lookup, nested_update
from constant import filter_columns, EDITOR_KEYS, TEMPERATURE_URL, SYSTEM_LOAD_URL, POWER_URL, GPU_TEMP_URL
from rest import Rest
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


    def action_items(self, table=None, name=None, device_type=None):
        """
        This method provide the action items for the table. 
        """
        ## Here we have two strategy to show action items. One with buttons and one with icons.
        ## I choose icons here with tooltips. If in future buttons are required instead of icons
        ## than set the value of items to button
        item_type = 'icon'
        if item_type == 'button':
            button = "btn btn-sm "
            info = f'<a href="/show/{table}/{name}" class="{button}btn-info">Info</a>'
            edit = f'<a href="/edit/{table}/{name}" class="{button}btn-primary">Edit</a>'
            if table == "inventory":
                delete = f'<a href="/delete/{table}/{name}/{device_type}" class="{button}btn-danger">Delete</a>'
            else:
                delete = f'<a href="/delete/{table}/{name}" class="{button}btn-danger">Delete</a>'
        elif item_type == 'icon':
            info =  self.make_icon(
                href=url_for('show', page=table, record=name),
                onclick=None,
                text=f'{name} Detail Information',
                icon='bx-info-circle',
                color='#03c3ec;'
            )
            edit =  self.make_icon(
                href=url_for('edit', page=table, record=name),
                onclick=None,
                text=f'Change in {name}',
                icon='bx-edit',
                color='#696cff;'
            )
            if table == "inventory":
                delete =  self.make_icon(
                    href=url_for('delete', page=table, record=name, device=device_type),
                    onclick=f'return confirm(\'Are you sure you want to delete {name}?\');',
                    text=f'Delete {name}',
                    icon='bx-trash',
                    color='red;'
                )
            else:
                delete =  self.make_icon(
                    href=url_for('delete', page=table, record=name),
                    onclick=f'return confirm(\'Are you sure you want to delete {name}?\');',
                    text=f'Delete {name}',
                    icon='bx-trash',
                    color='red;'
                )
        else:
            info = ''
            edit = ''
            delete = ''
        # response = "&nbsp;".join([edit, delete])
        if table == 'rack':
            response = "&nbsp;".join([info, edit, delete])
        else:
            response = "&nbsp;".join([edit, delete])
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


    def filter_data_list(self, table=None, data=None):
        """
        This method will generate the data as for row format
        """
        fields, rows, colored_fields = [], [], []
        fields = filter_columns(table)
        for field_key in fields:
            val_row = []
            for each in data:
                for key, value in each.items():
                    if field_key == key:
                        val_row.append(self.format_value(value))
            rows.append(val_row)
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
            action = self.action_items(table, row[0], row[1])
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


    def get_metrics(self, metric=None, data=None):
        """
        This method will retrieve the metrics from prometheus.
        How to Use:
        Add prometheus query URL in constants file and add one more elif condition in here.
        In rack.html & show.html CTRL+F: <a class="dropdown-item" href="" data-target="power_scale">Power Consumption</a>
        And add one more scale for new element.
        Then find: <code class="load-{{ each_device['name'] }}" data-bs-toggle="tooltip" data-bs-html="true" data-bs-placement="top">&nbsp;&nbsp;&nbsp;</code>
        And add one more element for new entry. Now goto footer.js and modify prometheus.forEach(function(device) accordingly.
        """
        if metric == 'temperature':
            metric_url = TEMPERATURE_URL
        elif metric == 'load':
            metric_url = SYSTEM_LOAD_URL
        elif metric == 'power':
            metric_url = POWER_URL
        elif metric == 'gpu_temp':
            metric_url = GPU_TEMP_URL
        else:
            metric_url = None
        if metric_url:
            get_data = Rest().get_url_data(route=metric_url)
            if get_data is not False:
                try:
                    request_data = get_data.json()
                except requests.exceptions.JSONDecodeError:
                    request_data = {"status": "JSONDecodeError"}
                if request_data["status"] == "success":
                    for values in request_data["data"]["result"]:
                        hostname = values["metric"]["hostname"]
                        luna_group = values["metric"]["luna_group"]
                        value = values["value"]
                        metric_value = value[1]
                        if data:
                            for check in data:
                                if check['hostname'] == hostname:
                                    check[metric] = value[1]
                                else:
                                    data.append({'hostname': hostname, 'type': luna_group, metric: metric_value})
                        else:
                            data.append({'hostname': hostname, 'type': luna_group, metric: metric_value})
        return data

