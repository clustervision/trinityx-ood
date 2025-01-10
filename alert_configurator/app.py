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
This File is a Main File Alert Configurator.
This file will provide the functionality to configure and manage the monitoring alerts for nodes.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from constant import LICENSE, TOKEN_FILE, TRIX_CONFIG
from log import Log
from rest import Rest


LOGGER = Log.init_log('INFO')
TABLE = 'monitor'
TABLE_CAP = 'Alert Configurator'
app = Flask(__name__, static_folder="nhc/assets", template_folder="nhc")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app, resources={r"/get_rules": {"origins": "http://localhost:5173"}})
CORS(app, resources={r"/save_config": {"origins": "http://localhost:5173"}})
CORS(app, resources={r"/save_nodes": {"origins": "http://localhost:5173"}})
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
    promQLurl   = "https://vmware-controller1.cluster:9090"
    appUrl      = "http://vmware-controller1.cluster:7755"
    statusAPI   = "https://vmware-controller1.cluster:9090/api/v1/rules"
    ResetNode   = "https://vmware-controller1.cluster:7050/import/prometheus_nhc_rules"
    return render_template("index.html", promQLurl=promQLurl, appUrl=appUrl, statusAPI=statusAPI, ResetNode=ResetNode)


@app.route('/get_nodes', methods=['GET'])
def get_nodes():
    """
    This method to show the monitor status and queue.
    """
    status, response = Rest().get_luna_nodes()
    node_list = []
    if 'config' in response:
        for node in response["config"]["node"]:
            node_list.append(node)
    print(node_list)
    if status is True:
        return jsonify(node_list), 200
    else:
        return jsonify(node_list), 400
    


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
    app.run(host='0.0.0.0', port=7755, debug= True)
    # app.run()
