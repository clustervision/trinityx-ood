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
from textwrap import wrap
from html import unescape
from flask import Flask, render_template, request, flash, url_for, redirect, jsonify
import requests
import urllib3
from flask_cors import CORS
from rest import Rest
from constant import LICENSE, TOKEN_FILE, APP_STATE
from log import Log
from helper import Helper
from presenter import Presenter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGER = Log.init_log('INFO')
TABLE = 'rack'
TABLE_CAP = 'Rack'
# app = Flask(__name__, static_folder="static")
app = Flask(__name__, static_folder="app/assets", template_folder="app")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

if APP_STATE is False: # FOR Development Only
    CORS(app, resources={r"/get_nodes": {"origins": "http://localhost:5173"}})
    CORS(app, resources={r"/manage": {"origins": "http://localhost:5173"}})
    CORS(app, resources={r"/show": {"origins": "http://localhost:5173"}})
    CORS(app, resources={r"/update": {"origins": "http://localhost:5173"}})
    CORS(app, resources={r"/edit": {"origins": "http://localhost:5173"}})
    CORS(app, resources={r"/delete": {"origins": "http://localhost:5173"}})
    CORS(app, resources={r"/perform": {"origins": "http://localhost:5173"}})
    CORS(app, resources={r"/license": {"origins": "http://localhost:5173"}})


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
    This is the main method of application. It will Show Monitor Options.
    """
    url = Helper().app_url(request)
    print(url)
    return render_template("index.html", PROMETHEUS_URL=url['PROMETHEUS_URL'], APP_URL=url['APP_URL'])


@app.route('/get_nodes/<string:rack_name>', methods=['GET'])
def get_nodes(rack_name=None):
    """
    This route will call the prometheus URL to collect the temperature for the machines.
    """
    response = {"status": False, "message": []}
    table_data = Rest().get_data(TABLE, rack_name)
    if isinstance(table_data, dict):
        rack_data = table_data["config"]["rack"][rack_name]["devices"]
        for node in rack_data:
            if node["type"] == "node":
                response["status"] = True
                response["message"].append(node["name"])
    print(jsonify(response))
    return jsonify(response)


@app.route('/manage_racks', methods=['GET'])
def manage_racks():
    """
    This is the main route to manage things.
    """
    response = {"status": False, "message": []}
    table_data = Rest().get_data(TABLE)
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config']['rack']
        response["status"] = True
        response["message"].append(raw_data)
    print(jsonify(response))
    return jsonify(response)


@app.route('/manage_inventory', methods=['GET'])
def manage_inventory():
    """
    This is the main route to manage things.
    """
    response = {"status": False, "message": []}
    table_data = Rest().get_data(TABLE, "inventory")
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config']['rack']["inventory"]
        response["status"] = True
        response["message"] = raw_data
    print(jsonify(response))
    return jsonify(response)


@app.route('/show_rack/<string:rack_name>', methods=['GET'])
def show_rack(rack_name: str):
    """
    This route will return the provided rack data.
    """
    response = {"status": False, "message": {}}
    table_data = Rest().get_data(TABLE, rack_name)
    if table_data:
        rack_data = table_data["config"]["rack"][rack_name]
        response["message"] = rack_data
    print(jsonify(response))
    return jsonify(response)


@app.route('/change_rack', methods=['POST'])
def change_rack():
    """
    This route will be used to update the rack from Manage Rack.
    """
    response = {"status": False, "message": ""}
    payload = {}
    if request.method == 'POST':
        payload = {
            k: v
            for k, v in request.form.items() if v not in [None, '']
        }
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        post_response = Rest().post_data(TABLE, payload['name'], request_data)
        LOGGER.info(f'{post_response.status_code} -> {post_response.content}')
        if post_response.status_code == 204:
            response = {"status": True, "message": f'{TABLE_CAP}, {payload["name"]} Updated.'}
        else:
            response_json = post_response.json()
            response["message"] = f'HTTP ERROR :: {post_response.status_code} - {response_json["message"]}'
    print(jsonify(response))
    return jsonify(response)


@app.route('/change_inventory', methods=['POST'])
def change_inventory():
    """
    This route will be used to update the inventory from Manage Inventory.
    """
    response = {"status": False, "message": ""}
    payload = {}
    if request.method == 'POST':
        payload = {
            k: v
            for k, v in request.form.items() if v not in [None, '']
        }
        payload = Helper().prepare_payload(None, payload)
        request_data = { 'config': { TABLE: { "inventory": [payload] } } }
        post_response = Rest().post_data(TABLE, "inventory", request_data)
        LOGGER.info(f'{post_response.status_code} -> {post_response.content}')
        if post_response.status_code == 204:
            response = {"status": True, "message": f'{TABLE_CAP}, {payload["name"]} Updated.'}
        else:
            response_json = post_response.json()
            response["message"] = f'HTTP ERROR :: {post_response.status_code} - {response_json["message"]}'
    print(jsonify(response))
    return jsonify(response)



# @app.route('/update', methods=['POST']) # TODOD Need to update the logic
# def update():
#     """
#     This API route will update the position of a device in a rack.
#     """
#     payload = {}
#     request_data = json.loads(request.get_json())
#     if request_data['rack']:
#         rack_name = request_data['rack']
#         del request_data['rack']
#         payload = {'config': {'rack': {rack_name: {'devices': [request_data]} } } }
#         uri = f'config/rack/{rack_name}'
#         result = Rest().post_raw(uri, payload)
#     else:
#         uri = f'inventory/{request_data["name"]}/type/{request_data["type"]}'
#         result = Rest().get_delete(TABLE, uri)
#         LOGGER.info(f'Response {result.content} & HTTP Code {result.status_code}')
#     response = json.dumps(payload)
#     return response

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
    if APP_STATE is False:
        dev_context=(
            '/trinity/local/etc/ssl/vmware-controller1.cluster.crt',
            '/trinity/local/etc/ssl/vmware-controller1.cluster.key'
        )
        app.run(host='0.0.0.0', port=7755, debug= True, ssl_context=dev_context)
    else:
        app.run()

# Run in Dev mode:
# sudo setfacl -m u:admin:r /trinity/local/etc/ssl/vmware-controller1.cluster.*
# sudo -u admin bash -c '. /trinity/local/python/bin/activate && python app.py'
