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
This File is a Main File Luna 2 Node.
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
from flask import Flask,request, render_template, flash, url_for, redirect
from rest import Rest
from constant import LICENSE, TOKEN_FILE, APP_STATE
from helper import Helper
from presenter import Presenter
from log import Log
from model import Model

LOGGER = Log.init_log('INFO')
TABLE = 'node'
TABLE_CAP = 'Node'
app = Flask(__name__, static_folder="static")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

if APP_STATE is False: 
    app.config["DEBUG"] = True
    os.environ["FLASK_ENV"] = "development"


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


@app.errorhandler(404)
def page_not_found(e):
    """
    This method will redirect to error Template Page with Error Message on 404.
    """
    return render_template("error.html", table=TABLE_CAP, data="", error=f"ERROR :: {e}"), 200


@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application. It will list all Nodes which is available with daemon.
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
    group_list = Model().get_list_option_html('group')
    bmcsetup_list = Model().get_list_option_html('bmcsetup')
    switch_list = Model().get_list_option_html('switch')
    osimage_list = Model().get_list_option_html('osimage')
    network_list = Model().get_list_option_html('network')
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload["service"] = True if 'service' in payload else False
        payload["setupbmc"] = True if 'setupbmc' in payload else False
        payload["netboot"] = True if 'netboot' in payload else False
        payload["bootmenu"] = True if 'bootmenu' in payload else False
        table_data = Rest().get_data(TABLE, payload['name'])
        if table_data:
            if payload['name'] in table_data['config'][TABLE]:
                error = f'HTTP ERROR :: {payload["name"]} is already present in the database.'
                flash(error, "error")
                return redirect(url_for('add'), code=302)
        payload = Helper().prepare_payload(None, payload)
        for k, v in payload.items():
            if v == 'on':
                payload[k] = True
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
        return render_template("add.html", table=TABLE_CAP, switch_list=switch_list, bmcsetup_list=bmcsetup_list, osimage_list=osimage_list, network_list=network_list, group_list=group_list, page=page)


@app.route('/rename/<string:record>', methods=['GET', 'POST'])
def rename(record=None):
    """
    This method will Rename the Node.
    """
    data = {}
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload['name'] = payload['name']
        payload['newnodename'] = payload['newname']
        del payload['newname']
        response = Helper().update_record(TABLE, payload)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            flash(f'{TABLE_CAP} renamed from {payload["name"]} to {payload["newnodename"]}.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('rename', record=payload['newnodename']), code=302)
    elif request.method == 'GET':
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        if table_data:
            raw_data = table_data['config'][TABLE][record]
            data = {'name': raw_data['name'], 'newname': ''}
    return render_template("rename.html", table=TABLE_CAP, data=data)


@app.route('/nextip_network/<string:network>', methods=['GET'])
def nextip_network(network=None):
    """
    Method to show a network in Luna Configuration.
    """
    response = None
    uri = f'{network}/_nextfreeip'
    nextip = Rest().get_data('network', uri)
    if nextip:
        response = nextip['config']['network'][network]['nextip']
    return response


@app.route('/edit/<string:record>', methods=['GET', 'POST'])
def edit(record=None):
    """
    This Method will add a requested record.
    """
    data = {}
    bmcsetup_list, osimage_list, interface_html, group_list = '', '', '', ''
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        data = table_data['config'][TABLE][record]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
        if 'bmcsetup' in data:
            if 'bmcsetup_source' in data:
                bmcsetup_list = Model().get_list_option_html('bmcsetup', data['bmcsetup'], data['bmcsetup_source'])
            elif '_bmcsetup_source' in data:
                bmcsetup_list = Model().get_list_option_html('bmcsetup', data['bmcsetup'], data['_bmcsetup_source'])
            else:
                bmcsetup_list = Model().get_list_option_html('bmcsetup', data['bmcsetup'])
        else:
            bmcsetup_list = Model().get_list_option_html('bmcsetup')
        if 'osimage' in data:
            if 'osimage_source' in data:
                osimage_list = Model().get_list_option_html('osimage', data['osimage'], data['osimage_source'])
            elif '_osimage_source' in data:
                osimage_list = Model().get_list_option_html('osimage', data['osimage'], data['_osimage_source'])
            else:
                osimage_list = Model().get_list_option_html('osimage', data['osimage'])
        else:
            osimage_list = Model().get_list_option_html('osimage')
        if 'group' in data:
            group_list = Model().get_list_option_html('group', data['group'])
        else:
            group_list = Model().get_list_option_html('group')
        if 'switch' in data:
            switch_list = Model().get_list_option_html('switch', data['switch'])
        else:
            switch_list = Model().get_list_option_html('switch')

        selected_modes = {
            'selected_none': '',
            'selected_rr': '',
            'selected_ab': '',
            'selected_xor': '',
            'selected_broadcast': '',
            'selected_8023ad': '',
            'selected_tlb': '',
            'selected_alb': ''
        }

        raw_html = Template("""
            <div class="input-group">
                <span class="input-group-text">Interface</span>
                <input type="text" name="interface" required class="form-control" maxlength="100" id="id_interface" value="$interface" />
                <span class="input-group-text">Network</span>
                <select name="network" class="form-control" id="id_network">$network</select>
                <span class="input-group-text btn btn-sm btn-success" id="raw_network">Ip address</span>
                <input type="text" name="ipaddress" class="form-control ipv4" maxlength="100" id="id_ipaddress" inputmode="decimal" value="$ipaddress" />
                <span class="input-group-text">Mac address</span>
                <input type="text" name="macaddress" class="form-control mac" maxlength="100" id="id_macaddress" inputmode="text" value="$macaddress" />
                <span class="input-group-text">Options</span>
                <input type="text" name="options" class="form-control" maxlength="100" id="id_options" value="$options" />
                <span class="input-group-text">VLAN ID</span>
                <input type="number" name="vlanid" min="0" max="4094" class="form-control" placeholder="VLAN ID" value="$vlanid" />
                <span class="input-group-text">VLAN Parent</span>
                <input type="text" name="vlan_parent" class="form-control" placeholder="VLAN Parent" value="$vlan_parent" />
                <span class="input-group-text">Bond Mode</span>
                <select name="bond_mode" class="form-control">
                    <option value='' ${selected_none}>--- Select Bond Mode ---</option>
                    <option value='balance-rr' ${selected_rr}>balance-rr</option>
                    <option value='active-backup' ${selected_ab}>active-backup</option>
                    <option value='balance-xor' ${selected_xor}>balance-xor</option>
                    <option value='broadcast' ${selected_broadcast}>broadcast</option>
                    <option value='802.3ad' ${selected_8023ad}>802.3ad</option>
                    <option value='balance-tlb' ${selected_tlb}>balance-tlb</option>
                    <option value='balance-alb' ${selected_alb}>balance-alb</option>
                </select>
                <span class="input-group-text">Bond Slaves</span>
                <input type="text" name="bond_slaves" class="form-control" placeholder="Bond Slaves Interfaces" value="${bond_slaves}" />
                <span class="input-group-text">DHCP&nbsp;
                    <input type="checkbox" class="form-check-input" id="id_dhcp" $dhcp_checked onclick="toggleDHCP(this)" />
                    <input type="hidden" name="dhcp" value="$dhcp" />
                </span>
                $button
              </div><br />""")
        interface_html = ""
        remove_button = '<button type="button" class="btn btn-sm btn-danger" id="remove_nodeinterface">Remove Interface</button>'
        if 'interfaces' in data:
            interface_list = []
            for interfaces in data['interfaces']:
                if 'interface' in interfaces:
                    interface_list.append(interfaces['interface'])

            for interface_dict in data['interfaces']:
                interface = interface_dict['interface'] if 'interface' in interface_dict else ""
                ipaddress = interface_dict['ipaddress'] if 'ipaddress' in interface_dict else ""
                macaddress = interface_dict['macaddress'] if 'macaddress' in interface_dict else ""
                macaddress = "" if macaddress is None else macaddress
                network = Model().get_list_option_html('network', interface_dict['network']) if 'network' in interface_dict else Model().get_list_option_html('network')
                options = interface_dict['options'] if 'options' in interface_dict else ""
                vlanid = interface_dict['vlanid'] if 'vlanid' in interface_dict else ""
                vlan_parent = interface_dict['vlan_parent'] if 'vlan_parent' in interface_dict else ""
                bond_mode = interface_dict['bond_mode'] if 'bond_mode' in interface_dict else ""
                bond_slaves = interface_dict['bond_slaves'] if 'bond_slaves' in interface_dict else ""
                dhcp = interface_dict['dhcp'] if 'dhcp' in interface_dict else ""
                dhcp_checked = "checked" if dhcp is True else ""

                selected_key = {
                    '': 'selected_none',
                    'balance-rr': 'selected_rr',
                    'active-backup': 'selected_ab',
                    'balance-xor': 'selected_xor',
                    'broadcast': 'selected_broadcast',
                    '802.3ad': 'selected_8023ad',
                    'balance-tlb': 'selected_tlb',
                    'balance-alb': 'selected_alb'
                }.get(bond_mode, 'selected_none')

                selected_modes[selected_key] = 'selected'

                interface_html += raw_html.safe_substitute(interface=interface, ipaddress=ipaddress, macaddress=macaddress, network=network, options=options, vlanid=vlanid, vlan_parent=vlan_parent, **selected_modes, bond_mode=bond_mode, bond_slaves=bond_slaves, dhcp_checked=dhcp_checked, dhcp=dhcp, button=remove_button)
        else:
            interface_html = raw_html.safe_substitute(interface='', network=Model().get_list_option_html('network'), options='', button=remove_button)
        interface_html = interface_html[:-6]
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None]}
        payload = Helper().prepare_payload(None, payload)
        payload["service"] = True if 'service' in payload else False

        if '(group)' in payload['osimage']:
            payload['osimage'] = ''
        else:
            if '(' in payload['osimage'] and ')' in payload['osimage']:
                payload['osimage'] = payload['osimage'].split('(', 1)[0]

        if '(group)' in payload['bmcsetup']:
            payload['bmcsetup'] = ''
        else:
            if '(' in payload['bmcsetup'] and ')' in payload['bmcsetup']:
                payload['bmcsetup'] = payload['bmcsetup'].split('(', 1)[0]

        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, TABLE, payload)
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
        return render_template("edit.html", table=TABLE_CAP, record=record,  data=data, switch_list=switch_list, bmcsetup_list=bmcsetup_list, osimage_list=osimage_list, interface_html=interface_html, group_list=group_list)


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
    bmcsetup_list, osimage_list, interface_html, group_list = '', '', '', ''
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        data = table_data['config'][TABLE][record]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
        if 'bmcsetup' in data:
            if 'bmcsetup_source' in data:
                bmcsetup_list = Model().get_list_option_html('bmcsetup', data['bmcsetup'], data['bmcsetup_source'])
            elif '_bmcsetup_source' in data:
                bmcsetup_list = Model().get_list_option_html('bmcsetup', data['bmcsetup'], data['_bmcsetup_source'])
            else:
                bmcsetup_list = Model().get_list_option_html('bmcsetup', data['bmcsetup'])
        else:
            bmcsetup_list = Model().get_list_option_html('bmcsetup')
        if 'osimage' in data:
            if 'osimage_source' in data:
                osimage_list = Model().get_list_option_html('osimage', data['osimage'], data['osimage_source'])
            elif '_osimage_source' in data:
                osimage_list = Model().get_list_option_html('osimage', data['osimage'], data['_osimage_source'])
            else:
                osimage_list = Model().get_list_option_html('osimage', data['osimage'])
        else:
            osimage_list = Model().get_list_option_html('osimage')
        if 'group' in data:
            group_list = Model().get_list_option_html('group', data['group'])
        else:
            group_list = Model().get_list_option_html('group')
        if 'switch' in data:
            switch_list = Model().get_list_option_html('switch', data['switch'])
        else:
            switch_list = Model().get_list_option_html('switch')
        
        selected_modes = {
            'selected_none': '',
            'selected_rr': '',
            'selected_ab': '',
            'selected_xor': '',
            'selected_broadcast': '',
            'selected_8023ad': '',
            'selected_tlb': '',
            'selected_alb': ''
        }

        raw_html = Template("""
            <div class="input-group">
                <span class="input-group-text">Interface</span>
                <input type="text" name="interface" class="form-control" maxlength="100" id="id_interface" value="$interface" />
                <span class="input-group-text">Network</span>
                <select name="network" class="form-control" id="id_network">$network</select>
                <span class="input-group-text btn btn-sm btn-success" id="raw_network" data-bs-toggle="tooltip" data-bs-offset="0,4" data-bs-placement="top" data-bs-html="true" data-bs-original-title="<i class='bx bx-info-circle bx-xs'></i> <span>Next Available IP Address </span>">Ip address</span>
                <input type="text" name="ipaddress" class="form-control ipv4" maxlength="100" id="id_ipaddress" inputmode="decimal" value="$ipaddress" />
                <span class="input-group-text">Mac address</span>
                <input type="text" name="macaddress" class="form-control mac" maxlength="100" id="id_macaddress" inputmode="text" value="" />
                <span class="input-group-text">Options</span>
                <input type="text" name="options" class="form-control" maxlength="100" id="id_options" value="$options" />
                <span class="input-group-text">VLAN ID</span>
                <input type="number" name="vlanid" min="0" max="4094" class="form-control" placeholder="VLAN ID" value="$vlanid" />
                <span class="input-group-text">VLAN Parent</span>
                <input type="text" name="vlan_parent" class="form-control" placeholder="VLAN Parent" value="$vlan_parent" />
                <span class="input-group-text">Bond Mode</span>
                <select name="bond_mode" class="form-control">
                    <option value='' ${selected_none}>--- Select Bond Mode ---</option>
                    <option value='balance-rr' ${selected_rr}>balance-rr</option>
                    <option value='active-backup' ${selected_ab}>active-backup</option>
                    <option value='balance-xor' ${selected_xor}>balance-xor</option>
                    <option value='broadcast' ${selected_broadcast}>broadcast</option>
                    <option value='802.3ad' ${selected_8023ad}>802.3ad</option>
                    <option value='balance-tlb' ${selected_tlb}>balance-tlb</option>
                    <option value='balance-alb' ${selected_alb}>balance-alb</option>
                </select>
                <span class="input-group-text">Bond Slaves</span>
                <input type="text" name="bond_slaves" class="form-control" placeholder="Bond Slaves Interfaces" value="${bond_slaves}" />
                <span class="input-group-text">DHCP&nbsp;
                    <input type="checkbox" class="form-check-input" id="id_dhcp" $dhcp_checked onclick="toggleDHCP(this)" />
                    <input type="hidden" name="dhcp" value="$dhcp" />
                </span>
                $button
              </div><br />""")
        interface_html = ""
        remove_button = '<button type="button" class="btn btn-sm btn-danger" id="remove_nodeinterface">Remove Interface</button>'
        if 'interfaces' in data:
            interface_list = []
            for interfaces in data['interfaces']:
                if 'interface' in interfaces:
                    interface_list.append(interfaces['interface'])

            for interface_dict in data['interfaces']:
                interface = interface_dict['interface'] if 'interface' in interface_dict else ""
                macaddress = interface_dict['macaddress'] if 'macaddress' in interface_dict else ""
                macaddress = "" if macaddress is None else macaddress
                network = Model().get_list_option_html('network', interface_dict['network']) if 'network' in interface_dict else Model().get_list_option_html('network')
                ipaddress = nextip_network(interface_dict['network']) if 'ipaddress' in interface_dict else ""
                options = interface_dict['options'] if 'options' in interface_dict else ""
                vlanid = interface_dict['vlanid'] if 'vlanid' in interface_dict else ""
                vlan_parent = interface_dict['vlan_parent'] if 'vlan_parent' in interface_dict else ""
                bond_mode = interface_dict['bond_mode'] if 'bond_mode' in interface_dict else ""
                bond_slaves = interface_dict['bond_slaves'] if 'bond_slaves' in interface_dict else ""
                dhcp = interface_dict['dhcp'] if 'dhcp' in interface_dict else ""
                dhcp_checked = "checked" if dhcp is True else ""

                selected_key = {
                    '': 'selected_none',
                    'balance-rr': 'selected_rr',
                    'active-backup': 'selected_ab',
                    'balance-xor': 'selected_xor',
                    'broadcast': 'selected_broadcast',
                    '802.3ad': 'selected_8023ad',
                    'balance-tlb': 'selected_tlb',
                    'balance-alb': 'selected_alb'
                }.get(bond_mode, 'selected_none')

                selected_modes[selected_key] = 'selected'

                interface_html += raw_html.safe_substitute(interface=interface, ipaddress=ipaddress, network=network, options=options, vlanid=vlanid, vlan_parent=vlan_parent, **selected_modes, bond_mode=bond_mode, bond_slaves=bond_slaves, dhcp_checked=dhcp_checked, dhcp=dhcp, button=remove_button)
        else:
            interface_html = raw_html.safe_substitute(interface='', network=Model().get_list_option_html('network'), options='', button=remove_button)
        interface_html = interface_html[:-6]
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload["service"] = True if 'service' in payload else False
        payload = Helper().prepare_payload(None, payload)

        if '(group)' in payload['osimage']:
            payload['osimage'] = ''
        else:
            if '(' in payload['osimage'] and ')' in payload['osimage']:
                payload['osimage'] = payload['osimage'].split('(', 1)[0]

        if '(group)' in payload['bmcsetup']:
            payload['bmcsetup'] = ''
        else:
            if '(' in payload['bmcsetup'] and ')' in payload['bmcsetup']:
                payload['bmcsetup'] = payload['bmcsetup'].split('(', 1)[0]

        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, TABLE, payload)
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_clone(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 201:
            flash(f'{TABLE_CAP}, {data["name"]} Cloned as {payload["newnodename"]}.', "success")
            return redirect(url_for('edit', record=payload['newnodename']), code=302)
        else:
            try:
                response_json = response.json()
                error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            except json.decoder.JSONDecodeError:
                error = f'HTTP ERROR :: {response.status_code} - {response.content}'
            flash(error, "error")
        return redirect(url_for('clone', record=record), code=302)
    else:
        return render_template("clone.html", table=TABLE_CAP, record=record,  data=data, switch_list=switch_list, bmcsetup_list=bmcsetup_list, osimage_list=osimage_list, interface_html=interface_html, group_list=group_list)


@app.route('/osgrab/<string:record>', methods=['GET', 'POST'])
def osgrab(record=None):
    """
    This method will open the Login Page(First Page)
    """
    data = {}
    osimage_list = ''
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        request_data = {'config':{TABLE:{payload['name']: payload}}}
        uri = f'config/{TABLE}/{payload["name"]}/_osgrab'
        response = Rest().post_raw(uri, request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        response_json = response.json()
        if response.status_code == 200:
            flash(response_json['message'], "success")
            if 'request_id' in response_json:
                return redirect(url_for('osgrab', record = record, request_id=response_json['request_id'], message=response_json['message']), code=302)
        else:
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('osgrab', record=record), code=302)

    elif request.method == 'GET':
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        node_list = Model().get_list_option_html('node', record)
        if table_data:
            raw_data = table_data['config'][TABLE][record]
            data = Helper().prepare_json(raw_data)
            osimage_list = Model().get_list_option_html('osimage', data['osimage'])
    return render_template("osgrab.html", table=TABLE_CAP, record=record,  data=data, node_list=node_list, osimage_list=osimage_list)


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
        LOGGER.info(f'{response.status_code} {response.content}')
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
        node_list = Model().get_list_option_html('node', record)
        if table_data:
            raw_data = table_data['config'][TABLE][record]
            data = Helper().prepare_json(raw_data)
            osimage_list = Model().get_list_option_html('osimage', data['osimage'])
    return render_template("ospush.html", table=TABLE_CAP, record=record,  data=data, node_list=node_list, osimage_list=osimage_list)


@app.route('/check_status/<string:status>/status/<string:request_id>', methods=['GET'])
def check_status(status=None, request_id=None):
    """
    This method will check the status of request on behalf of request ID.
    """
    response = {"message": "No Response"}
    if request:
        uri = f'{status}/status/{request_id}'
        result = Rest().get_raw(uri)
        LOGGER.info(f'{result.status_code} {result.content}')
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
        app.run(host='0.0.0.0', port=7755, debug=True)
    else:
        app.run()
