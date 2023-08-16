#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


    def daemon_status(self):
        """
        This method will check if daemon is working or not.
        """
        response =  Rest().get_data('cluster')
        if response:
            response = response['config']['cluster']
        else:
            response = None
        return response


    def filter_interfaces(self, request=None, table=None, payload=None):
        """
        This method
        """
        post_list = dict(request.POST)
        interface_list, interface = [], {}
        if table == 'node':
            if 'ipaddress' not in post_list:
                post_list["ipaddress"] = [None] * len(post_list["interface"])
            if 'macaddress' not in post_list:
                post_list["macaddress"] =  [None] * len(post_list["interface"])
        if 'network' not in post_list:
            post_list["network"] =  [None] * len(post_list["interface"])
        if 'options' not in post_list:
            post_list["options"] =  [None] * len(post_list["interface"])
        if table == 'node':
            zip_interface = zip(
                post_list["interface"],
                post_list["ipaddress"],
                post_list["macaddress"],
                post_list["network"],
                post_list["options"]
            )
            for list_interface, ipaddress, macaddress, network, options in zip_interface:
                if list_interface:
                    interface['interface'] = list_interface
                if ipaddress:
                    interface['ipaddress'] = ipaddress
                if macaddress:
                    interface['macaddress'] = macaddress
                if network:
                    interface['network'] = network
                if options:
                    interface['options'] = options
                if list_interface:
                    interface_list.append(interface)
                interface = {}
        elif table =='group':
            zip_interface = zip(post_list["interface"], post_list["network"], post_list["options"])
            for list_interface, network, options in zip_interface:
                if list_interface:
                    interface['interface'] = list_interface
                if network:
                    interface['network'] = network
                if options:
                    interface['options'] = options
                if list_interface:
                    interface_list.append(interface)
                interface = {}
        if 'interface' in payload:
            del payload['interface']
        if table == 'node':
            if 'ipaddress' in payload:
                del payload['ipaddress']
            if 'macaddress' in payload:
                del payload['macaddress']
        if 'network' in payload:
            del payload['network']
        if 'options' in payload:
            del payload['options']
        payload['interfaces'] = interface_list
        return payload


    def statistics(self):
        """
        This method will fetch the node and cluster cpu usage.
        """
        response = []
        labels = []
        dataset  = ""
        route = 'http://localhost:8086/query?db=telegraf'
        payload = 'SELECT usage_idle FROM "cpu" WHERE time > now() - 1h GROUP BY host LIMIT 10;'
        payload = urllib.parse.quote(payload)
        route = f'{route}&q={payload}'
        influx_data = Rest().get_url_data(route, payload=None)
        if influx_data:
            if influx_data.status_code == 200:
                result = influx_data.json()
                date_format = '%Y-%m-%dT%H:%M:%SZ'
                if 'series' in result['results'][0]:
                    for host in result['results'][0]['series']:
                        status = {}
                        status['data'] = []
                        status['host'] = host['tags']['host']
                        for formatting in host['values']:
                            date_formatted = str(datetime.strptime(formatting[0], date_format))
                            value = str(int(formatting[1]))
                            status['data'].append({'x': date_formatted, 'y': int(value)})
                            labels.append(date_formatted)
                        response.append(status)
        num = 1
        labels = list(dict.fromkeys(labels))
        for each in response:
            if num == 1:
                color = '"#ff3e1d"'
            else:
                color = f'"{self.get_color()}"'
            dataset += f"""
            {{
                data: {each["data"]},
                label: "{each["host"]}",
                borderColor: {color},
                tension: .5,
                pointStyle: "circle",
                backgroundColor: {color},
                fill: !1,
                pointRadius: 1,
                pointHoverRadius: 5,
                pointHoverBorderWidth: 5,
                pointBorderColor: "transparent",
                pointHoverBorderColor: i,
                pointHoverBackgroundColor: {color}
            }},
            """
            num = num + 1
        return labels, dataset


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
        # TODO
        # Nested Update is updating all values of the same key name,
        # Need to figure out the solution.
        # For example; While updating the node with multiple interfaces which have the different
        # option values, is updating first option value to the each option.
        # raw_data = self.choice_to_bool(raw_data)
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
        for ele in data:
            if 'name' in data[ele]:
                name = data[ele]["name"]
            elif 'username' in data[ele]:
                name = data[ele]["username"]
            elif 'groupname' in data[ele]:
                name = data[ele]["groupname"]
            if name:
                action = self.action_items(table, name)
                for row in rows:
                    if name in row:
                        row.insert(len(row), action)
                        name = ""
        # Adding Serial Numbers to the dataset
        fields.insert(0, 'S. No.')
        fields.insert(len(fields),"Actions")
        num = 1
        for outer in rows:
            outer.insert(0, num)
            num = num + 1
        # Adding Serial Numbers to the dataset
        if table == 'power':
            head = '<input type="checkbox" id="selectAll" />'
            fields.insert(0, head)
            num = 1
            for outer in rows:
                checkbox = f'<input type="checkbox" name="node" value="{outer[1]}"  id="{num}" />'
                outer.insert(0, checkbox)
                num = num + 1
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
            status = f'<a href="/power/status/{name}" class="{button}btn-info">Status</a>'
            turn_on  = f'<a href="/power/on/{name}" class="{button}btn-primary">Power ON</a>'
            off = f'<a href="/power/off/{name}" class="{button}btn-danger">Power OFF</a>'
            # info = f'<a href="/info/{table}/{name}" class="{button}btn-info">Info</a>'
            info = f'<a href="/show/{name}" class="{button}btn-info">Info</a>'
            # edit = f'<a href="/edit/{table}/{name}" class="{button}btn-primary">Edit</a>'
            edit = f'<a href="/edit/{name}" class="{button}btn-primary">Edit</a>'
            # delete = f'<a href="/delete/{table}/{name}" class="{button}btn-danger">Delete</a>'
            delete = f'<a href="/delete/{name}" class="{button}btn-danger">Delete</a>'
            # clone = f'<a href="/clone/{table}/{name}" class="{button}btn-warning">Clone</a>'
            clone = f'<a href="/clone/{name}" class="{button}btn-warning">Clone</a>'
            member_click = f'onclick="member(\'osimage\', \'{name}\');"'
            member_button = f'class="{button}rounded-pill btn-outline-primary"'
            member = f'<button type="button" {member_click} {member_button}>Member Nodes</button>'
            pack_click = f'onclick="pack_osimage(\'{name}\');"'
            pack = f'<button type="button" {pack_click} class="{button}btn-secondary">Pack</button>'
            kernel = f'<a href="/kernel/{table}/{name}" class="{button}btn-dark">Change Kernel</a>'
            osgrab = f'<a href="/osgrab/{table}/{name}" class="{button}btn-secondary">Grab OS</a>'
            ospush = f'<a href="/ospush/{table}/{name}" class="{button}btn-dark">OS Push</a>'
            taken_click = f'onclick="taken(\'{name}\');"'
            taken_button = f'class="{button}rounded-pill btn-outline-primary"'
            taken = f'<button type="button" {taken_click} {taken_button}>Reserved IP</button>'
            ipinfo = f'<a href="/ipinfo/{table}/{name}" class="{button}btn-secondary">IP Info</a>'
            nextip = f'<a href="/nextip/{table}/{name}" class="{button}btn-dark">Next IP</a>'
        elif item_type == 'icon':
            status =  self.make_icon(
                href=f"/power/status/{name}",
                onclick=None,
                text=f'Current Status of {name}',
                icon='bx-stats',
                color='#03c3ec;'
            )
            turn_on =  self.make_icon(
                href=f"/power/on/{name}",
                onclick=None,
                text=f'Power ON {name}',
                icon='bx-power-off',
                color='#71dd37;'
            )
            off =  self.make_icon(
                href=f"/power/off/{name}",
                onclick=None,
                text=f'Power OFF {name}',
                icon='bx-power-off bx-flip-vertical',
                color='#ff3e1d;'
            )
            info =  self.make_icon(
                # href=f"/info/{table}/{name}",
                href=url_for('show', record=name),
                # href=f"/show/{name}",
                onclick=None,
                text=f'{name} Detail Information',
                icon='bx-info-circle',
                color='#03c3ec;'
            )
            edit =  self.make_icon(
                # href=f"/edit/{table}/{name}",
                # href=f"/edit/{name}",
                href=url_for('edit', record=name),
                onclick=None,
                text=f'Change in {name}',
                icon='bx-edit',
                color='#696cff;'
            )
            delete =  self.make_icon(
                # href=f"/delete/{table}/{name}",
                # href=f"/delete/{name}",
                href=url_for('delete', record=name),
                onclick=f'return confirm(\'Are you sure you want to delete {name}?\');',
                text=f'Delete {name}',
                icon='bx-trash',
                color='red;'
            )
            # clone =  self.make_icon(
            #     # href=f"/clone/{table}/{name}",
            #     # href=f"/clone/{name}",
            #     href=url_for('clone', record=name),
            #     onclick=None,
            #     text=f'Clone {name}',
            #     icon='bx-duplicate',
            #     color='#20c997;'
            # )
            member =  self.make_icon(
                href=None,
                onclick=f'member(\'{table}\', \'{name}\');',
                text=f'Member Nodes of {name}',
                icon='bx-copy-alt',
                color='#007bff;'
            )
            pack =  self.make_icon(
                href=None,
                onclick=f'member(\'osimage\', \'{name}\');',
                text=f'Pack {name}',
                icon='bx-package',
                color='#8592a3;'
            )
            kernel =  self.make_icon(
                href=f"/kernel/{table}/{name}",
                onclick=None,
                text=f'Change Kernel Of {name}',
                icon='bx-microchip',
                color='#697a8d;'
            )
            osgrab =  self.make_icon(
                href=f"/osgrab/{table}/{name}",
                onclick=None,
                text=f'Grab OS for {name}',
                icon='bx-package',
                color='#8592a3;'
            )
            ospush =  self.make_icon(
                href=f"/ospush/{table}/{name}",
                onclick=None,
                text=f'Push OS for {name}',
                icon='bxs-package',
                color='#697a8d;'
            )
            taken =  self.make_icon(
                href=None,
                onclick=f'taken(\'{name}\');',
                text=f'Reserved IP with {name}',
                icon='bx-list-ol',
                color='#007bff;'
            )
            ipinfo =  self.make_icon(
                # href=f"/ipinfo/{table}/{name}",
                href=url_for('ipinfo', record=name),
                onclick=None,
                text=f'IP Information on {name}',
                icon='bx-subdirectory-left',
                color='#fd7e14;'
            )
            nextip =  self.make_icon(
                # href=f"/nextip/{table}/{name}",
                href=url_for('nextip', record=name),
                onclick=None,
                text=f'Next Available IP on {name}',
                icon='bx-subdirectory-right',
                color='#ffab00;'
            )
        else:
            status = ''
            turn_on  = ''
            off = ''
            info = ''
            edit = ''
            delete = ''
            clone = ''
            member = ''
            pack = ''
            kernel = ''
            osgrab = ''
            ospush = ''
            taken = ''
            ipinfo = ''
            nextip = ''
        action = {
            # 'power':    [status, turn_on, off],
            # 'node':     [info, edit, delete, clone, osgrab, ospush],
            # 'group':    [info, edit, delete, clone, member, ospush],
            # 'bmcsetup': [info, edit, delete, clone, member],
            # 'switch':   [info, edit, delete, clone],
            # 'otherdev': [info, edit, delete, clone],
            # 'osimage':  [info, edit, delete, clone, member, pack, kernel],
            'network':  [info, edit, delete, taken, ipinfo, nextip]#,
            # 'groupsecrets': [info, edit, delete, clone],
            # 'nodesecrets':  [info, edit, delete, clone],
            # 'osuser': [info, edit, delete],
            # 'osgroup':  [info, edit, delete]
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
            action = self.action_items(table, f'{outer[0]}JOIN-NODENAME-SECRETNAME{outer[1]}')
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
            new_fields.append("")
            new_row.append("")
        return new_fields, new_row


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
