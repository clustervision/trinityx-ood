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
from flask import Flask, render_template
from rest import Rest
from constant import LICENSE
from log import Log
from helper import Helper
from presenter import Presenter
from model import Model

LOGGER = Log.init_log('INFO')
TABLE = 'rack'
TABLE_CAP = 'Monitor'
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
    print("------------------")
    print("show")
    print(page)
    print(record)
    print("------------------")


@app.route('/edit/<string:page>', methods=['GET'])
@app.route('/edit/<string:page>/<string:record>', methods=['GET'])
def edit(page=None, record=None):
    data, error = "", ""
    # site_list = Model().get_list_options('network')
    site_list = ''
    
    if page == "rack":
        table_data = Rest().get_data(TABLE, record)
    else:
        table_data = Rest().get_data(TABLE, page)
    print(table_data)
    if table_data:
        if page == "rack":
            data = table_data["config"]["rack"][record]
        else:
            tmp_data = table_data["config"]["rack"][page]
            for each in tmp_data:
                if each['name'] == record:
                    data = each

    else:
        data = {}
    print("------------------")
    print("edit")
    print(page)
    print(record)
    print(data)
    print("------------------")

    page_cap = page.capitalize()
    return render_template("change.html", page=page_cap, record=record, data=data, site_list=site_list, error=error)

@app.route('/delete/<string:page>/<string:record>', methods=['GET'])
def delete(page=None, record=None):
    print("------------------")
    print("delete")
    print(page)
    print(record)
    print("------------------")

@app.route('/status/<string:service>', methods=['GET'])
def status(service=None):
    """
    This method to show the monitor status and queue.
    """
    response = ''
    data = Rest().get_raw('monitor', service)
    if data.content:
        data = data.content.decode("utf-8")
        data = json.loads(data)
        data = data['monitor'][service]
        if data:
            fields, rows  = Helper().filter_interface(service, data)
            fields = list(map(lambda x: x.replace('username_initiator', 'Initiate By'), fields))
            fields = list(map(lambda x: x.replace('request_id', 'Request ID'), fields))
            fields = list(map(lambda x: x.replace('read', 'Read'), fields))
            fields = list(map(lambda x: x.replace('message', 'Message'), fields))
            fields = list(map(lambda x: x.replace('created', 'Created On'), fields))
            fields = list(map(lambda x: x.replace('username_initiator', 'Initiate By'), fields))
            fields = list(map(lambda x: x.replace('level', 'Level'), fields))
            fields = list(map(lambda x: x.replace('status', 'Status'), fields))
            fields = list(map(lambda x: x.replace('subsystem', 'Sub System'), fields))
            fields = list(map(lambda x: x.replace('task', 'Task'), fields))
            data = Presenter().show_table(fields, rows)
            response = unescape(data)
        else:
            response = f'<center><strong style="color: blue;">Monitor {service} is empty.</strong></center>'
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
    app.run(host= '0.0.0.0', port= 7059, debug= True)
    # app.run()
