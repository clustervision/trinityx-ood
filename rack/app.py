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
This File is a Main File Luna 2 Monitor.
This file will provide the functionality to observe the Luna status and queue.
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
from textwrap import wrap
from html import unescape
from flask import Flask, render_template, request, flash, url_for, redirect, jsonify
from rest import Rest
from constant import LICENSE
from log import Log
from helper import Helper
from presenter import Presenter
from model import Model

LOGGER = Log.init_log('INFO')
TABLE = 'rack'
TABLE_CAP = 'Rack'
app = Flask(__name__, static_url_path='/')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application. It will Show Monitor Options.
    """
    table_data = Rest().get_data(TABLE)
    if table_data:
        rack_data = table_data["config"]["rack"]
    else:
        rack_data = {}
    table_data = Rest().get_data(TABLE, "inventory/unconfigured")
    if table_data:
        inventory = table_data["config"]["rack"]["inventory"]
    else:
        inventory = {}
    return render_template("rack.html", table=TABLE_CAP, rack_data=rack_data, inventory=inventory, rack_size=52, title='Status', data=None)


@app.route('/get_screen_size', methods=['POST'])
def get_screen_size():
    data = request.json
    width = data['width']
    if width >= 1921:
        width = 220
    else:
        width = 120
    height = data['height']
    # Process screen size data as needed
    print(f"Screen Width: {width}, Screen Height: {height}")
    # return 'Screen size received successfully'
    # return jsonify({'width': width})
    return f'{width}'


@app.route('/manage/<string:page>', methods=['GET'])
def manage(page=None):
    """
    This is the main route to manage things.
    """
    # nav = types.SimpleNamespace()
    # nav.name = f"Manage {TABLE_CAP}"
    table_data = Rest().get_data(TABLE, "inventory/unconfigured")
    if table_data:
        inventory = table_data["config"]["rack"]["inventory"]
    else:
        inventory = {}
    data, error = "", ""
    if page == "site":
        table_data = {"config": {"rack": {"site": [{"name": "ClusterVision Amsterdam", "rooms": 2}, {"name": "ClusterVision Schiphol", "rooms": 3}] } } }
    elif page == "room":
        table_data = {"config": {"rack": {"room": [
            {"name": "Basement", "site": "ClusterVision Amsterdam", "racks": 20}, {"name": "1st Floor", "site": "ClusterVision Amsterdam", "racks": 10},
            {"name": "Basement", "site": "ClusterVision Schiphol", "racks": 10}, {"name": "1st Floor", "site": "ClusterVision Schiphol", "racks": 20}, {"name": "2nd Floor", "site": "ClusterVision Schiphol", "racks": 30}
            ] } } }
    elif page == "rack":
        table_data = Rest().get_data(TABLE)
    elif page == "inventory":
        table_data = Rest().get_data(TABLE, "inventory")

    LOGGER.info(table_data)
    if table_data:
        if page in ["site", "room", "inventory"]:
            raw_data = table_data['config']['rack'][page]
            fields, rows  = Helper().filter_data_list(page, raw_data)
        elif page == "rack":
            raw_data = table_data['config']['rack']
            fields, rows  = Helper().filter_data(page, raw_data)
        data = Presenter().show_table(fields, rows)
        data = unescape(data)

    if page in ["site", "room", "rack", "inventory"]:
        page_cap = page.capitalize()
    return render_template("manage.html", table=TABLE_CAP, page=page_cap, inventory=inventory, data=data, error=error)


@app.route('/show/<string:page>/<string:record>', methods=['GET'])
def show(page=None, record=None):
    table_data = Rest().get_data(TABLE, record)
    if table_data:
        rack_data = table_data["config"]["rack"][record]
    else:
        rack_data = {}
    table_data = Rest().get_data(TABLE, "inventory/unconfigured")
    if table_data:
        inventory = table_data["config"]["rack"]["inventory"]
    else:
        inventory = {}
    page_cap = page.capitalize()
    return render_template("show.html", table=TABLE_CAP, page=page_cap, record=record, rack_data=rack_data, inventory=inventory, rack_size=52, title='Status')


@app.route('/update', methods=['POST'])
def update():
    """
    This API route will update the position of a device in a rack.
    """
    payload = {}
    request_data = json.loads(request.get_json())
    if request_data['rack']:
        rack_name = request_data['rack']
        del request_data['rack']
        payload = {'config': {'rack': {rack_name: {'devices': [request_data]} } } }
        uri = f'config/rack/{rack_name}'
        result = Rest().post_raw(uri, payload)
    else:
        uri = f'inventory/{request_data["name"]}/type/{request_data["type"]}'
        result = Rest().get_delete(TABLE, uri)
        print(f'Response {result.content} & HTTP Code {result.status_code}')
    response = json.dumps(payload)
    return response


@app.route('/edit/<string:page>', methods=['GET', 'POST'])
@app.route('/edit/<string:page>/<string:record>', methods=['GET', 'POST'])
def edit(page=None, record=None):
    data, error = "", ""
    site_list = ''
    if page.lower() == "rack":
        table_data = Rest().get_data(TABLE, record)
    else:
        table_data = Rest().get_data(TABLE, page)
    if table_data:
        if page.lower() == "rack":
            if record in table_data["config"]["rack"]:
                data = table_data["config"]["rack"][record]
        else:
            tmp_data = table_data["config"]["rack"][page]
            for each in tmp_data:
                if each['name'] == record:
                    data = each
    else:
        data = {}
    payload = {}
    if request.method == 'POST':
        payload = {
            k: v
            for k, v in request.form.items() if v not in [None, '']
        }
        payload = Helper().prepare_payload(None, payload)
        if page.lower() == "rack":
            payload['size'] = int(payload['size'])
            request_data = {'config': {TABLE: {payload['name']: payload}}}
        else:
            request_data = { 'config': { TABLE: { "inventory": [payload] } } }
        if page.lower() == "rack":
            if table_data:
                if payload['name'] in table_data['config'][TABLE]:
                    if 'devices' in table_data['config'][TABLE][payload['name']]:
                        if table_data['config'][TABLE][payload['name']]['devices']:
                            if table_data['config'][TABLE][payload['name']]['order'] != payload['order']:
                                error = "Rack have devices, Kindly remove them before changing the Order of Rack"
                                flash(error, "danger")
                                return redirect(url_for('edit', page=page, record=record), code=302)
                            if table_data['config'][TABLE][payload['name']]['size'] != payload['size']:
                                error = "Rack have devices, Kindly remove them before changing the Size of Rack"
                                flash(error, "danger")
                                return redirect(url_for('edit', page=page, record=record), code=302)

            response = Rest().post_data(TABLE, payload['name'], request_data)
        else:
            configured = Rest().get_data(TABLE, "inventory/configured")
            if 'config' in configured:
                inventory = configured['config']['rack']['inventory']
                for each in inventory:
                    if each['name'] == payload['name'] and each['type'] == payload['type']:
                        if int(each['height']) != int(payload['height']):
                            error = "Inventory is configured in a Rack, Kindly remove it from there to change the height."
                            flash(error, "danger")
                            return redirect(url_for('edit', page=page, record=record), code=302)
                        if each['orientation'] != payload['orientation']:
                            error = "Inventory is configured in a Rack, Kindly remove it from there to change the orientation."
                            flash(error, "danger")
                            return redirect(url_for('edit', page=page, record=record), code=302)
            response = Rest().post_data(TABLE, page, request_data)
        LOGGER.info(f'{response.status_code} -> {response.content}')
        if response.status_code == 204:
            flash(f'{TABLE_CAP}, {payload["name"]} Updated.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "danger")
        return redirect(url_for('edit', page=page, record=record), code=302)
    page_cap = page.capitalize()

    
    table_data = Rest().get_data(TABLE, "inventory/unconfigured")
    if table_data:
        inventory = table_data["config"]["rack"]["inventory"]
    else:
        inventory = {}
    return render_template("change.html", table=TABLE_CAP, page=page_cap, record=record, data=data, inventory=inventory, site_list=site_list, error=error)


@app.route('/delete/<string:page>/<string:record>', methods=['GET'])
@app.route('/delete/<string:page>/<string:record>/<string:device>', methods=['GET'])
def delete(page=None, record=None, device=None):
    if page == "rack":
        response = Rest().get_delete(TABLE, record)
    else:
        response = Rest().get_delete(TABLE, f'inventory/{record}/type/{device}')
    LOGGER.info(f'{response.status_code} -> {response.content}')
    if response.status_code == 204:
        flash(f'{TABLE_CAP}, {record} is deleted.', "success")
    elif response.status_code == 201:
        response_json = response.json()
        flash(response_json["message"], "success")
    else:
        response_json = response.json()
        flash(f'ERROR {response.status_code} :: {response_json["message"]}', "danger")
    return redirect(url_for('manage', page=page), code=302)


@app.route('/perform/<string:system>/<string:action>/<string:nodename>', methods=['GET'])
def perform(system=None, action=None, nodename=None):
    """
    This is the main method of application.
    It will list all Control which is available with daemon.
    """
    response = {"status": "danger", "message": ""}
    message = ''
    if system and action and nodename:
        uri = f'control/action/{system}/{nodename}/_{action}'
        result = Rest().get_raw(uri)
        if result.content:
            content = result.json()
            if 'control' in content.keys():
                message = content['control'][system]
            elif 'message' in content.keys():
                message = content['message']
            else:
                message = 'NO message received'
        else:
            message = action
        if len(message) >= 150:
            message = '<br />'.join(wrap(message, width=150))
            message = f'<br />{message}'
        if result.status_code in [200, 204]:
            if 'off' in message:
                response['status'] = "danger"
                response['message'] = f'<strong>Node {nodename} {system} {action} :: {message}.</strong>'
            else:
                response['status'] = "success"
                response['message'] = f'<strong>Node {nodename} {system} {action} :: {message}.</strong>'
        else:
            response['status'] = "warning"
            response['message'] = f'<strong>{nodename} {system} {action} :: {message}.</strong>'
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
    # app.run(host='0.0.0.0', port=7059, debug=True)
    app.run()
