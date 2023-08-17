#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

from flask import Flask, json, request, render_template, flash
from rest import Rest
from log import Log

logger = Log.init_log('DEBUG')
app = Flask(__name__, static_url_path='/')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    This is the main method of application. It will list all Services and perform operations.
    """
    table = 'service'
    response = None
    if request.method == "POST":
        response = service_status(request.form['service'], request.form['action'])
        if 'implemented' in response.lower():
            flash(f'{request.form["service"]}, {response}.', "warning")
        elif 'fail' in response.lower() or 'not' in response.lower():
            flash(f'{request.form["service"]}, {response}.', "error")
        else:
            flash(f'{request.form["service"]}, {response}.', "success")
    current_state = {}
    current_state['dhcp'] = service_status('dhcp', 'status')
    current_state['dns'] = service_status('dns', 'status')
    current_state['luna2'] = service_status('luna2', 'status')
    return render_template("service.html", table = table.capitalize(), current_state = current_state, response = response)


@app.route('/get_request/<string:status>/<string:service_name>/<string:action>', methods=['GET'])
def get_request(status=None, service_name=None, action=None):
    """
    This method will fetch the raw data from the daemon.
    """
    response = {"message": "No Response"}
    if request:
        uri = f'{status}/{service_name}/{action}'
        result = Rest().get_raw(uri)
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
        uri = f'service/status/{request_id}'
        result = Rest().get_raw(uri)
        response = result.json()
    response = json.dumps(response)
    return response


def service_status(service_name=None, action=None):
    """
    Method to will perform the action on the desired service by Luna Daemon's API.
    """
    uri = f'service/{service_name}/{action}'
    response = Rest().get_raw(uri)
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


if __name__ == "__main__":
    # app.run(host= '0.0.0.0', port= 7059, debug= True)
    app.run()
