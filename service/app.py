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
This File is a Main File Luna 2 Service.
This file will create flask object and serve the all routes for on demand.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

import os
from flask import Flask, json, request, render_template, flash
from rest import Rest
from constant import LICENSE, TOKEN_FILE
from log import Log

LOGGER = Log.init_log('INFO')
TABLE = 'service'
TABLE_CAP = 'Service'
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


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    This is the main method of application. It will list all Services and perform operations.
    """
    response = None
    if request.method == "POST":
        response = service_status(request.form['service'], request.form['action'])
        if 'implemented' in response.lower():
            flash(f'{request.form[TABLE]}, {response}.', "warning")
        elif 'fail' in response.lower() or 'not' in response.lower():
            flash(f'{request.form[TABLE]}, {response}.', "error")
        else:
            flash(f'{request.form[TABLE]}, {response}.', "success")
    current_state = {}
    current_state['dhcp'] = service_status('dhcp', 'status')
    current_state['dns'] = service_status('dns', 'status')
    current_state['luna2'] = service_status('luna2', 'status')
    LOGGER.info(current_state)
    return render_template("service.html", current_state=current_state, response=response, table=f'Manage {TABLE_CAP}', data=None)


@app.route('/get_request/<string:status>/<string:service_name>/<string:action>', methods=['GET'])
def get_request(status=None, service_name=None, action=None):
    """
    This method will fetch the raw data from the daemon.
    """
    response = {"message": "No Response"}
    if request:
        uri = f'{status}/{service_name}/{action}'
        result = Rest().get_raw(uri)
        LOGGER.info(f'{result.status_code} {result.content}')
        response = result.json()
    response = json.dumps(response)
    return response


@app.route('/check_status/<string:request_id>', methods=['GET'])
def check_status(request_id=None):
    """
    This method will check the status of request on behalf of request ID.
    """
    response = {"message": "No Response"}
    if request:
        uri = f'{TABLE}/status/{request_id}'
        result = Rest().get_raw(uri)
        LOGGER.info(f'{result.status_code} {result.content}')
        response = result.json()
    response = json.dumps(response)
    return response


def service_status(service_name=None, action=None):
    """
    Method to will perform the action on the desired service by Luna Daemon's API.
    """
    uri = f'{TABLE}/{service_name}/{action}'
    response = Rest().get_raw(uri)
    LOGGER.info(f'{response.status_code} {response.content}')
    if not isinstance(response, bool):
        status_code = response.status_code
        content = response.json()
        if status_code == 200:
            if 'info' in content:
                response = content["info"]
            else:
                service_name = list(content['monitor']['Service'].keys())
                response = content['monitor']['Service'][service_name[0]]
        elif status_code == 503:
            service_name = list(content['monitor']['Service'].keys())
            response = content['monitor']['Service'][service_name[0]]
        else:
            response = content
    else:
        response = "Luna 2 Daemon is not Running."
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
    # app.run(host= '0.0.0.0', port= 7059, debug= True)
    app.run()
