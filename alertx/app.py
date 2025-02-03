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
This File is a Main File AlertX.
This file will provide the functionality to configure and manage the monitoring alerts for nodes.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2025, TrinityX[AlertX]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

import os
from flask import Flask, render_template, request, jsonify
from constant import LICENSE, APP_STATE
from log import Log
from rest import Rest
from helper import Helper


LOGGER = Log.init_log('INFO')
TABLE = 'monitor'
TABLE_CAP = 'Alert Configurator'
app = Flask(__name__, static_folder="app/assets", template_folder="app")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
if APP_STATE is False: # FOR Development Only
    from flask_cors import CORS 
    CORS(app, resources={r"/get_rules": {"origins": "http://localhost:5173"}})
    CORS(app, resources={r"/save_config": {"origins": "http://localhost:5173"}})
    CORS(app, resources={r"/license": {"origins": "http://localhost:5173"}})
    CORS(app, resources={r"/get_nodes": {"origins": "http://localhost:5173"}})
    CORS(app, resources={r"/save_nodes": {"origins": "http://localhost:5173"}})


@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application. It will Show Monitor Options.
    """
    url = Helper().app_url(request)
    return render_template("index.html", PROMQL_URL=url['PROMQL_URL'], APP_URL=['APP_URL'])


@app.route('/get_nodes', methods=['GET'])
def get_nodes():
    """
    This method to show the monitor status and queue.
    """
    status, response = Rest().get_luna_nodes()
    node_list = []
    if 'config' in response:
        for _, details in response["config"]["node"].items():
            node_list.append(details["hostname"])
        if (node_list):
            node_list = ",".join(node_list)
            status, response = Rest().get_node_hw(nodes = node_list)
    if status is True:
        return jsonify(response), 200
    else:
        return jsonify(response), 400
    

@app.route('/save_config', methods=['POST'])
def save_config():
    """
    This method to show the monitor status and queue.
    """
    status, response = Rest().post_rules(data=request.json)
    return jsonify({"response": response}), status


@app.route('/get_rules', methods=['GET'])
def get_rules():
    """
    This method to show the monitor status and queue.
    """
    check, configuration = Rest().get_rules()
    if check is True:
        return jsonify(configuration), 200
    else:
        return jsonify(configuration), 400


@app.route('/save_nodes', methods=['POST'])
def save_nodes():
    """
    This method save the Node hardware.
    """
    status, response = Rest().post_nodes(data=request.json)
    return jsonify({"response": response}), status


@app.route('/get_global', methods=['GET'])
def get_global():
    """
    This method will get the global settings for the Node Hardware.
    """
    check, setting = Rest().get_global_hw()
    if check is True:
        return jsonify(setting), 200
    else:
        return jsonify(setting), 400


@app.route('/set_global', methods=['POST'])
def set_global():
    """
    This method will save the global settings for the Node Hardware.
    """
    status, response = Rest().post_global_hw(data=request.json)
    return jsonify({"response": response}), status


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
