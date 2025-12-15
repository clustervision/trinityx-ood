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
This File is a Main File Luna 2 Rack View.
This file will provide the functionality to manage the Rack and the inventory in it.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2026, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Production'

import os
import json
from textwrap import wrap
from flask import Flask, render_template, request, jsonify
import urllib3
from flask_cors import CORS
from rest import Rest
from constant import LICENSE, TOKEN_FILE, APP_STATE, APP_KEY
from log import Log
from helper import Helper

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGER = Log.init_log('INFO')
app = Flask(__name__, static_folder="app/assets", template_folder="app")
app.secret_key = APP_KEY

if APP_STATE is False: # FOR Development Only
    CORS(app, resources = {r"/get_nodes":           {"origins": "http://localhost:5173"}} )
    CORS(app, resources = {r"/manage_racks":        {"origins": "http://localhost:5173"}} )
    CORS(app, resources = {r"/manage_inventory":    {"origins": "http://localhost:5173"}} )
    CORS(app, resources = {r"/show_rack":           {"origins": "http://localhost:5173"}} )
    CORS(app, resources = {r"/change_rack":         {"origins": "http://localhost:5173"}} )
    CORS(app, resources = {r"/change_inventory":    {"origins": "http://localhost:5173"}} )
    CORS(app, resources = {r"/delete_rack":         {"origins": "http://localhost:5173"}} )
    CORS(app, resources = {r"/delete_inventory":    {"origins": "http://localhost:5173"}} )
    CORS(app, resources = {r"/update_rack":         {"origins": "http://localhost:5173"}} )
    CORS(app, resources = {r"/update_inventory":    {"origins": "http://localhost:5173"}} )
    CORS(app, resources = {r"/perform":             {"origins": "http://localhost:5173"}} )
    CORS(app, resources = {r"/license":             {"origins": "http://localhost:5173"}} )


@app.before_request
def validate_home_directory():
    """
    Validate the $HOME directory of the user before proceeding further.
    """
    if request.path.startswith('/static/'):
        return
    if "does not exist" in TOKEN_FILE:
        response = {"status": False, "message": TOKEN_FILE}
        return response
    return None


@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application. It will Show Monitor Options.
    """
    url = Helper().app_url(request)
    print(url)
    return render_template(
        "index.html",
        PROMETHEUS_URL  = url['PROMETHEUS_URL'],
        APP_URL         = url['APP_URL']
    )


@app.route('/device_pool', methods=['GET'])
def device_pool():
    """
    This is the main method of application. It will Show Monitor Options.
    """
    response = {"status": False, "message": []}
    table_data = Rest().get_data("rack", "inventory/unconfigured")
    if table_data:
        # response["message"] = table_data.content["config"]["rack"]["inventory"]
        response["message"] = table_data["config"]["rack"]["inventory"]
    print(jsonify(response))
    return jsonify(response)


@app.route('/get_nodes/<string:rack_name>', methods=['GET'])
def get_nodes(rack_name=None):
    """
    This route will call the prometheus URL to collect the temperature for the machines.
    """
    response = {"status": False, "message": []}
    table_data = Rest().get_data("rack", rack_name)
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
    table_data = Rest().get_data("rack")
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
    table_data = Rest().get_data("rack", "inventory")
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
    table_data = Rest().get_data("rack", rack_name)
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
        request_data = {'config': {"rack": {payload['name']: payload}}}
        post_response = Rest().post_data("rack", payload['name'], request_data)
        LOGGER.info("%s -> %s", post_response.status_code, post_response.content)
        if post_response.status_code == 204:
            response = {"status": True, "message": f'Rack, {payload["name"]} Updated.'}
        else:
            response_json = post_response.json()
            msg = f'HTTP ERROR :: {post_response.status_code} - {response_json["message"]}'
            response["message"] = msg
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
        request_data = { 'config': { "rack": { "inventory": [payload] } } }
        post_response = Rest().post_data("rack", "inventory", request_data)
        LOGGER.info("%s -> %s", post_response.status_code, post_response.content)
        if post_response.status_code == 204:
            response = {"status": True, "message": f'Rack, {payload["name"]} Updated.'}
        else:
            response_json = post_response.json()
            msg = f'HTTP ERROR :: {post_response.status_code} - {response_json["message"]}'
            response["message"] = msg
    print(jsonify(response))
    return jsonify(response)


@app.route('/delete_rack/<string:rack_name>', methods=['GET'])
def delete_rack(rack_name: str):
    """
    This route will remove the rack from the luna.
    """
    response = {"status": False, "message": ""}
    delete_response = Rest().get_delete("rack", rack_name)
    LOGGER.info("%s -> %s", delete_response.status_code, delete_response.content)
    if delete_response.status_code == 204:
        response = {"status": True, "message": f'Rack, {rack_name} is deleted.'}
    elif delete_response.status_code == 201:
        response_json = delete_response.json()
        response["message"] = response_json["message"]
    else:
        response_json = delete_response.json()
        response["message"] = f'ERROR {delete_response.status_code} :: {response_json["message"]}'
    print(jsonify(response))
    return jsonify(response)


@app.route('/delete_inventory/<string:device>/<string:inventory>', methods=['GET'])
def delete_inventory(device: str, inventory: str):
    """
    This route will remove the inventory from the luna.
    """
    response = {"status": False, "message": ""}
    delete_response = Rest().get_delete("rack", f'inventory/{inventory}/type/{device}')
    LOGGER.info("%s -> %s", delete_response.status_code, delete_response.content)
    if delete_response.status_code == 204:
        response = {"status": True, "message": f'Rack, {inventory} is deleted.'}
    elif delete_response.status_code == 201:
        response_json = delete_response.json()
        response["message"] = response_json["message"]
    else:
        response_json = delete_response.json()
        response["message"] = f'ERROR {delete_response.status_code} :: {response_json["message"]}'
    print(jsonify(response))
    return jsonify(response)


@app.route('/update_rack', methods=['POST'])
def update_rack():
    """
    This API route will update the position of a device in a rack.
    """
    response = {"status": False, "message": {}}
    payload = {}
    request_data = json.loads(request.get_json())
    rack_name = request_data['rack']
    del request_data['rack']
    payload = {'config': {'rack': {rack_name: {'devices': [request_data]} } } }
    uri = f'config/rack/{rack_name}'
    result = Rest().post_raw(uri, payload)
    LOGGER.info("Response %s & HTTP Code %s", result.status_code, result.content)
    response = {"status": True, "message": json.dumps(payload)}
    return jsonify(response)


@app.route('/update_inventory', methods=['POST'])
def update_inventory():
    """
    This API route will update the position of a device in a rack.
    """
    response = {"status": False, "message": {}}
    payload = {}
    request_data = json.loads(request.get_json())
    uri = f'inventory/{request_data["name"]}/type/{request_data["type"]}'
    result = Rest().get_delete("rack", uri)
    LOGGER.info("Response %s & HTTP Code %s", result.status_code, result.content)
    response = {"status": True, "message": json.dumps(payload)}
    return jsonify(response)


@app.route('/perform/<string:system>/<string:action>/<string:nodename>', methods=['GET'])
def perform(system=None, action=None, nodename=None):
    """
    This is the main method of application.
    It will list all Control which is available with daemon.
    """
    response = {"status": False, "message": ""}
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
                response['message'] = f'Node {nodename} {system} {action} :: {message}.'
            else:
                response['status'] = True
                response['message'] = f'Node {nodename} {system} {action} :: {message}.'
        else:
            response['message'] = f'{nodename} {system} {action} :: {message}.'
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
