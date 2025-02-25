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
This File is a Main File Luna 2 Group.
This file will create flask object and serve the all routes for on demand.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

import types
import os
import json
from string import Template
from html import unescape
from flask import Flask, request, render_template, flash, url_for, redirect
from rest import Rest
from constant import LICENSE, TOKEN_FILE, APP_STATE
from helper import Helper
from presenter import Presenter
from log import Log
from model import Model

LOGGER = Log.init_log('INFO')
TABLE = 'group'
TABLE_CAP = 'Group'
app = Flask(__name__, static_folder="static")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.before_request
def validate_home_directory():
    """
    Validate the $HOME directory of the user before proceeding further.
    """
    if request.path.startswith('/static/'):
        return
    if isinstance(TOKEN_FILE, dict):
        return render_template("error.html", table=TABLE_CAP, data="", error=TOKEN_FILE["error"])
    return None


@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application. It will list all Groups which is available with daemon.
    """
    data, error = "", ""
    table_data = Rest().get_data(TABLE)
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config'][TABLE]
        raw_data = Helper().prepare_json(raw_data, True)
        fields, rows  = Helper().filter_data(TABLE, raw_data)
        data = Presenter().show_table(fields, rows)
        data = unescape(data)
    else:
        error = f'No {TABLE_CAP} Available at this time.'
    return render_template("inventory.html", table=TABLE_CAP, data=data, error=error)


@app.route('/show/<string:record>', methods=['GET'])
def show(record=None):
    """
    This Method will show a specific record.
    """
    data, error = "", ""
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config'][TABLE][record]
        raw_data = Helper().prepare_json(raw_data)
        fields, rows  = Helper().filter_data_col(TABLE, raw_data)
        data = Presenter().show_table_col(fields, rows)
        data = unescape(data)
    else:
        error = f'{record} From {TABLE_CAP} is Not available at this time'
    return render_template("info.html", table=TABLE_CAP, data=data, error=error, record=record)


@app.route('/get_list/<string:table>', methods=['GET', 'POST'])
def get_list(table=None):
    """
    This method will return the list of element in table for as option for select tag.
    """
    response = None
    if request:
        response = Model().get_list_options(table)
        response = json.dumps(response)
    return response


@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    This Method will add a requested record.
    """
    page = types.SimpleNamespace()
    page.name = f"Add New {TABLE_CAP}"
    bmcsetup_list = Model().get_list_option_html('bmcsetup')
    osimage_list = Model().get_list_option_html('osimage')
    network_list = Model().get_list_option_html('network')
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        table_data = Rest().get_data(TABLE, payload['name'])
        if table_data:
            if payload['name'] in table_data['config'][TABLE]:
                error = f'HTTP ERROR :: {payload["name"]} is already present in the database.'
                flash(error, "error")
                return redirect(url_for('add'), code=302)
        payload = Helper().prepare_payload(None, payload)

        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, TABLE, payload)
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_data(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 201:
            flash(f'{TABLE_CAP}, {payload["name"]} Created.', "success")
            return redirect(url_for('home'), code=302)
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
            return redirect(url_for('add'), code=302)
    else:
        return render_template("add.html", table=TABLE_CAP, bmcsetup_list=bmcsetup_list, osimage_list=osimage_list, network_list=network_list, page=page)


@app.route('/rename/<string:record>', methods=['GET', 'POST'])
def rename(record=None):
    """
    This method will Rename the BMC Setup.
    """
    data = {}
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload['name'] = payload['name']
        payload['newgroupname'] = payload['newname']
        del payload['newname']
        response = Helper().update_record(TABLE, payload)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            flash(f'{TABLE_CAP} renamed to {payload["name"]}.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('rename', record=payload['newgroupname']), code=302)
    elif request.method == 'GET':
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        if table_data:
            raw_data = table_data['config'][TABLE][record]
            data = {'name': raw_data['name'], 'newname': ''}
    return render_template("rename.html", table=TABLE_CAP, data=data)


@app.route('/edit/<string:record>', methods=['GET', 'POST'])
def edit(record=None):
    """
    This Method will add a requested record.
    """
    data = {}
    bmcsetup_list, osimage_list, interface_html = '', '', ''
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        data = table_data['config'][TABLE][record]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
   
        if 'bmcsetupname' in data:
            bmcsetup_list = Model().get_list_option_html('bmcsetup', data['bmcsetupname'])
        else:
            bmcsetup_list = Model().get_list_option_html('bmcsetup')
        if 'osimage' in data:
            osimage_list = Model().get_list_option_html('osimage', data['osimage'])
        else:
            osimage_list = Model().get_list_option_html('osimage')

        raw_html = Template("""
            <div class="input-group">
                <span class="input-group-text">Interface</span>
                <input type="text" name="interface" required class="form-control" maxlength="100" id="id_interface" value="$interface" />
                <span class="input-group-text">Network</span>
                <select name="network" class="form-control" id="id_network">$network</select>
                <span class="input-group-text">VLAN ID</span>
                <input type="text" name="vlanid" class="form-control" placeholder="VLAN ID" value="$vlanid" />
                <span class="input-group-text">DHCP&nbsp;
                    <input type="checkbox" class="form-check-input" id="id_dhcp" $dhcp_checked onclick="toggleDHCP(this)" />
                    <input type="hidden" name="dhcp" value="$dhcp" />
                </span>
                <span class="input-group-text">Options</span>
                <input type="text" name="options" class="form-control" maxlength="100" id="id_options" value="$options" />
                $button
              </div><br />""")
        interface_html = ""
        remove_button = '<button type="button" class="btn btn-sm btn-danger" id="remove_nodeinterface">Remove Interface</button>'
        if 'interfaces' in data:
            for interface_dict in data['interfaces']:
                interface = interface_dict['interface'] if 'interface' in interface_dict else ""
                network = Model().get_list_option_html('network', interface_dict['network']) if 'network' in interface_dict else ""
                options = interface_dict['options'] if 'options' in interface_dict else ""
                vlanid = interface_dict['vlanid'] if 'vlanid' in interface_dict else ""
                dhcp = interface_dict['dhcp'] if 'dhcp' in interface_dict else ""
                dhcp_checked = "checked" if dhcp is True else ""
                interface_html += raw_html.safe_substitute(interface=interface, network=network, vlanid=vlanid, dhcp_checked=dhcp_checked, dhcp=dhcp, options=options, button=remove_button)
        interface_html = interface_html[:-6]
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None]}
        payload = Helper().prepare_payload(None, payload)
            
        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, TABLE, payload)
        
        if payload['bmcsetupname'] == '':
            del payload['bmcsetupname']
        if payload['osimage'] == '':
            del payload['osimage']
        if payload['osimagetag'] == '':
            del payload['osimagetag']
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_data(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            flash(f'{TABLE_CAP}, {payload["name"]} Updated.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('edit', record=record), code=302)
    else:
        return render_template("edit.html", table=TABLE_CAP, record=record,  data=data, bmcsetup_list=bmcsetup_list, osimage_list=osimage_list, interface_html=interface_html)


@app.route('/delete/<string:record>', methods=['GET'])
def delete(record=None):
    """
    This Method will delete a requested record.
    """
    response = Rest().get_delete(TABLE, record)
    LOGGER.info(f'{response.status_code} {response.content}')
    if response.status_code == 204:
        flash(f'{TABLE_CAP}, {record} is deleted.', "success")
    else:
        flash('ERROR :: Something went wrong!', "error")
    return redirect(url_for('home'), code=302)


@app.route('/remove/<string:record>/<string:interface>', methods=['GET'])
def remove(record=None, interface=None):
    """
    This Method will delete a requested record.
    """
    result = {}
    uri = record+'/interfaces/'+interface
    response = Rest().get_delete(TABLE, uri)
    LOGGER.info(f'{response.status_code} {response.content}')
    if response.status_code == 204:
        result['success'] = f'{interface} Deleted from {TABLE_CAP} {record}.'
    else:
        result['error'] = 'ERROR :: Something went wrong!'
    result = json.dumps(result)
    return result


@app.route('/clone/<string:record>', methods=['GET', 'POST'])
def clone(record=None):
    """
    This Method will clone a requested record.
    """
    data = {}
    bmcsetup_list, osimage_list, interface_html = '', '', ''
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        data = table_data['config'][TABLE][record]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
        if 'bmcsetupname' in data:
            bmcsetup_list = Model().get_list_option_html('bmcsetup', data['bmcsetupname'])
        else:
            bmcsetup_list = Model().get_list_option_html('bmcsetup')
        if 'osimage' in data:
            osimage_list = Model().get_list_option_html('osimage', data['osimage'])
        else:
            osimage_list = Model().get_list_option_html('osimage')

        raw_html = Template("""
            <div class="input-group">
                <span class="input-group-text">Interface</span>
                <input type="text" name="interface" class="form-control" maxlength="100" id="id_interface" value="$interface" />
                <span class="input-group-text">Network</span>
                <select name="network" class="form-control" id="id_network">$network</select>
                <span class="input-group-text">VLAN ID</span>
                <input type="text" name="vlanid" class="form-control" placeholder="VLAN ID" value="$vlanid" />
                <span class="input-group-text">DHCP&nbsp;
                    <input type="checkbox" class="form-check-input" id="id_dhcp" $dhcp_checked onclick="toggleDHCP(this)" />
                    <input type="hidden" name="dhcp" value="$dhcp" />
                </span>
                <span class="input-group-text">Options</span>
                <input type="text" name="options" class="form-control" maxlength="100" id="id_options" value="$options" />
                $button
              </div><br />""")
        interface_html = ""
        remove_button = '<button type="button" class="btn btn-sm btn-danger" id="remove_nodeinterface">Remove Interface</button>'
        if 'interfaces' in data:
            for interface_dict in data['interfaces']:
                interface = interface_dict['interface'] if 'interface' in interface_dict else ""
                network = Model().get_list_option_html('network', interface_dict['network']) if 'network' in interface_dict else ""
                options = interface_dict['options'] if 'options' in interface_dict else ""
                vlanid = interface_dict['vlanid'] if 'vlanid' in interface_dict else ""
                dhcp = interface_dict['dhcp'] if 'dhcp' in interface_dict else ""
                dhcp_checked = "checked" if dhcp is True else ""
                interface_html += raw_html.safe_substitute(interface=interface, network=network, vlanid=vlanid, dhcp_checked=dhcp_checked, dhcp=dhcp, options=options, button=remove_button)
        interface_html = interface_html[:-6]
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None]}
        payload = Helper().prepare_payload(None, payload)

        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, TABLE, payload)

        if payload['bmcsetupname'] == '':
            del payload['bmcsetupname']
        if payload['osimage'] == '':
            del payload['osimage']
        if payload['osimagetag'] == '':
            del payload['osimagetag']
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_clone(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 201:
            flash(f'{TABLE_CAP}, {data["name"]} Cloned as {payload["name"]}.', "success")
            return redirect(url_for('edit', record=payload['newgroupname']), code=302)
        else:
            try:
                response_json = response.json()
                error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            except json.decoder.JSONDecodeError:
                error = f'HTTP ERROR :: {response.status_code} - {response.content}'
            flash(error, "error")
        return redirect(url_for('clone', record=record), code=302)
    else:
        return render_template("clone.html", table=TABLE_CAP, record=record, data=data, bmcsetup_list=bmcsetup_list, osimage_list=osimage_list, interface_html=interface_html)


@app.route('/member/<string:table>/<string:record>', methods=['GET'])
def member(table=None, record=None):
    """
    This Method will provide all the member nodes for the requested record.
    """
    get_member = Rest().get_data(table, record+'/_member')
    LOGGER.info(get_member)
    if get_member:
        data = get_member['config'][table][record]['members']
        data = Helper().prepare_json(data)
        num = 1
        fields = ['S.No.', 'Nodes']
        rows = []
        for node in data:
            new_row = [num, node]
            rows.append(new_row)
            num = num + 1
        response = Presenter().show_table(fields, rows, True)
    else:
        response = f'{record} From {table.capitalize()} Not have any members at this time.'
    response = json.dumps(response)
    return response


@app.route('/ospush/<string:record>', methods=['GET', 'POST'])
def ospush(record=None):
    """
    This method will open the Login Page(First Page)
    """
    data = {}
    osimage_list = ''
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        request_data = {'config':{TABLE:{payload['name']: payload}}}
        uri = f'config/{TABLE}/{payload["name"]}/_ospush'
        response = Rest().post_raw(uri, request_data)
        response_json = response.json()

        if response.status_code == 200:
            flash(response_json['message'], "success")
            if 'request_id' in response_json:
                return redirect(url_for('ospush', record = record, request_id=response_json['request_id'], message=response_json['message']), code=302)
        else:
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('ospush', record=record), code=302)
    

    elif request.method == 'GET':
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        group_list = Model().get_list_option_html('group', record)
        if table_data:
            raw_data = table_data['config'][TABLE][record]
            data = Helper().prepare_json(raw_data)
            osimage_list = Model().get_list_option_html('osimage', data['osimage'])
    return render_template("osimage.html", table=TABLE_CAP, record=record, data=data, group_list=group_list, osimage_list=osimage_list)


@app.route('/check_status/<string:status>/status/<string:request_id>', methods=['GET'])
def check_status(status=None, request_id=None):
    """
    This method will check the status of request on behalf of request ID.
    """
    response = {"message": "No Response"}
    if request:
        uri = f'{status}/status/{request_id}'
        result = Rest().get_raw(uri)
        response = result.json()
    response = json.dumps(response)
    return response


@app.route('/license', methods=['GET'])
def license_info():
    """
    This Method will provide license in details.
    """
    response= 'LICENSE Information is not available at this moment.'
    file_check = os.path.isfile(LICENSE)
    read_check = os.access(LICENSE, os.R_OK)
    if file_check and read_check:
        with open(LICENSE, 'r', encoding="utf-8") as file_data:
            response = file_data.readlines()
            response = '<br />'.join(response)
    return response


if __name__ == "__main__":
    if APP_STATE is False: 
        app.run(host='0.0.0.0', port=7755, debug= True)
    else:
        app.run()

