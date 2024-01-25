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

import os
import json
from html import unescape
from flask import Flask, render_template, request, flash, url_for, redirect
from vsdx import VisioFile
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
    # vis = VisioFile('/home/sumit/Desktop/trinity-ood/rack/static/img/Lenovo-ThinkEdge.vssx')
    # vis = VisioFile('/home/sumit/Desktop/trinity-ood/rack/static/img/test4_connectors.vsdx')
    with VisioFile('/home/sumit/Desktop/trinity-ood/rack/static/img/test4_connectors.vsdx') as v:
        print(v.pages[0].connects)
    # print(vis)
    return render_template("rack.html", table=TABLE_CAP, rack_data=rack_data, inventory=inventory, rack_size=52, title='Status')


@app.route('/manage/<string:page>', methods=['GET'])
def manage(page=None):
    """
    This is the main route to manage things.
    """
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
    return render_template("manage.html", page=page_cap, data=data, error=error)


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
        print(payload)
        uri = f'config/rack/{rack_name}'
        result = Rest().post_raw(uri, payload)
        # result = result.json()
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
    # site_list = Model().get_list_options('network')
    site_list = ''
    if page.lower() == "rack":
        table_data = Rest().get_data(TABLE, record)
    else:
        table_data = Rest().get_data(TABLE, page)
    # print(table_data)
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
            # request_data = { 'config': { TABLE: { "inventory": [{ payload['name']: payload }] } } }
            request_data = { 'config': { TABLE: { "inventory": [payload] } } }
        if page.lower() == "rack":
            response = Rest().post_data(TABLE, payload['name'], request_data)
        else:
            print("-----------------------------------------------------------------------")
            print(TABLE)
            print(f'{page}/{payload["name"]}')
            print(request_data)
            print("-----------------------------------------------------------------------")
            # response = Rest().post_data(TABLE, f'{page}/{payload["name"]}', request_data)
            response = Rest().post_data(TABLE, page, request_data)
        print(TABLE)
        print(page)
        print(payload['name'])
        print(request_data)
        print(f'{response.status_code} -> {response.content}')
        LOGGER.info(f'{response.status_code} -> {response.content}')
        if response.status_code == 204:
            flash(f'{TABLE_CAP}, {payload["name"]} Updated.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('edit', page=page, record=record), code=302)
    page_cap = page.capitalize()
    return render_template("change.html",
                           page=page_cap,
                           record=record,
                           data=data,
                           site_list=site_list,
                           error=error)


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
    else:
        flash('ERROR :: Something went wrong!', "error")
    return redirect(url_for('manage', page=page), code=302)


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
    app.run(host='0.0.0.0', port=7059, debug=True)
    # app.run()
