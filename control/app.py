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
This File is a Main File Luna 2 Control Process.
This file will create flask object and serve the all routes for on demand.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

from textwrap import wrap
from flask import Flask, json, request, render_template, flash, url_for, redirect
from rest import Rest
from helper import Helper
from log import Log

LOGGER = Log.init_log('INFO')
TABLE = 'Control Nodes'
app = Flask(__name__, static_url_path='/')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/', methods=['GET'])
@app.route('/<string:system>/<string:action>/<string:nodename>', methods=['GET'])
def home(system=None, action=None, nodename=None):
    """
    This is the main method of application.
    It will list all Control which is available with daemon.
    """
    data, payload = [], []
    message = ''
    if action and nodename:
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
                flash(f'<strong>Node {nodename} {system} {action} :: {message}.</strong>', "danger")
            else:
                flash(f'<strong>Node {nodename} {system} {action} :: {message}.</strong>', "success")
        else:
            flash(f'<strong>{nodename} {system} {action} :: {message}.</strong>', "warning")
        return redirect(url_for('home'), code=302)

    node_list = Helper().get_name_list('node')

    if node_list:
        payload = json.dumps({'hostlist': node_list})
    else:
        flash('No Nodes are available at this time.', "error")
    return render_template("power.html", table=TABLE, data=data, payload= payload)


@app.route('/get_status', methods=['POST'])
def get_status():
    """
    This method will fetch the raw data from the daemon.
    """
    system = {'power': 'status', 'sel': 'list', 'chassis': 'identify'}
    request_data = json.loads(request.get_json())
    hostlist = request_data['hostlist']
    hostlist = Helper().collect_nodelist(hostlist)
    response = []
    for key, value in system.items():
        payload = {'control': {key: {value: {"hostlist": hostlist}}}}
        uri = f'control/action/{key}/_{value}'
        result = Rest().post_raw(uri, payload)
        result = result.json()
        response.append(result)
    response = json.dumps(response)
    return response


@app.route('/check_status/<string:power_id>/<string:sel_id>/<string:chassis_id>', methods=['GET'])
def check_status(power_id=None, sel_id=None, chassis_id=None):
    """
    This method will check the status of request on behalf of request ID.
    """
    response = []
    uri = f'control/status/{power_id}'
    result = Rest().get_raw(uri)
    LOGGER.info(f'{result.status_code} {result.content}')
    result = result.json()
    response.append(result)

    uri = f'control/status/{sel_id}'
    result = Rest().get_raw(uri)
    LOGGER.info(f'{result.status_code} {result.content}')
    result = result.json()
    response.append(result)

    uri = f'control/status/{chassis_id}'
    result = Rest().get_raw(uri)
    LOGGER.info(f'{result.status_code} {result.content}')
    result = result.json()
    response.append(result)

    response = json.dumps(response)
    return response


@app.route('/perform/<string:system>/<string:action>', methods=['POST'])
def perform(system=None, action=None):
    """
    This method will fetch the raw data from the daemon.
    """
    request_data = json.loads(request.get_json())
    hostlist = request_data['hostlist']
    hostlist = Helper().collect_nodelist(hostlist)
    payload = {'control': {system: {action: {"hostlist": hostlist}}}}
    uri = f'control/action/{system}/_{action}'
    result = Rest().post_raw(uri, payload)
    result = result.json()
    response = json.dumps(result)
    return response


@app.route('/check_request/<string:request_id>', methods=['GET'])
def check_request(request_id=None):
    """
    This method will check the status of request on behalf of request ID.
    """
    uri = f'control/status/{request_id}'
    result = Rest().get_raw(uri)
    LOGGER.info(f'{result.status_code} {result.content}')
    result = result.json()
    response = json.dumps(result)
    return response


if __name__ == "__main__":
    # app.run(host= '0.0.0.0', port= 7059, debug= True)
    app.run()
