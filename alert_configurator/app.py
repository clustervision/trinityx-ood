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
import json
from html import unescape
from flask import Flask, render_template, request, jsonify
from rest import Rest
from constant import LICENSE, TRIX_CONFIG
from log import Log
from helper import Helper
from presenter import Presenter

LOGGER = Log.init_log('INFO')
TABLE = 'monitor'
TABLE_CAP = 'Alert Configurator'
app = Flask(__name__, static_url_path='/')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application. It will Show Monitor Options.
    """
    # response = status('status')
    return render_template("configurator.html", table=TABLE_CAP, title='Status', TRIX_CONFIG=TRIX_CONFIG)


@app.route('/edit_config', methods=['GET'])
def edit_config():
    """
    This method to show the monitor status and queue.
    """
    response = Helper().load_yaml()
    return response


@app.route('/save_config', methods=['POST'])
def save_config():
    """
    This method to show the monitor status and queue.
    """
    try:
        yaml_data = request.json
        print(yaml_data)
        # yaml_data = Helper().json_to_yaml(json_data=data)
        # print(yaml_data)
        response = Helper().save_configuration(yaml_data=yaml_data)
        print(response)
    except Exception as exp:
        return jsonify({"response": str(exp)}), 400
    return jsonify({"response": "success"}), 200


@app.route('/get_rules', methods=['GET'])
def get_rules():
    """
    This method to show the monitor status and queue.
    """
    configuration = Helper().load_yaml()
    # print(configuration)
    # print(type(configuration))
    # response = configuration["groups"][0]["rules"]
    # return response
    return jsonify(configuration), 200



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
    app.run(host= '0.0.0.0', port= 7755, debug= True)
    app.run()
