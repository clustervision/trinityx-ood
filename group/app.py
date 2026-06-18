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
This File is a Main File Luna 2 Group.
This file will create flask object and serve the all routes for on demand.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

import types
import os
import json
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
import urllib3
from flask_cors import CORS
from rest import Rest
from constant import INI_FILE, LICENSE, TOKEN_FILE, APP_STATE
from helper import Helper
from log import Log
from model import Model

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGER = Log.init_log('INFO')
TABLE = 'group'
TABLE_CAP = 'Group'


def _group_write_payload():
    request_data = request.get_json()
    if not request_data:
        return None, (jsonify({"status": False, "message": "No JSON payload received"}), 400)
    return Helper().normalize_group_request(request_data), None

# Match node/osimage: expose bundle under /app/assets so punAppAssetUrl() paths resolve.
app = Flask(
    __name__,
    static_folder="app/assets",
    static_url_path="/app/assets",
    template_folder="app",
)

if APP_STATE is False:
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})


@app.before_request
def validate_home_directory():
    """
    Validate the $HOME directory of the user before proceeding further.
    """
    if request.path.startswith('/app/assets/'):
        return
    if isinstance(TOKEN_FILE, dict):
        return render_template("error.html", table='Group', data="", error=TOKEN_FILE["error"])
    file_check = os.path.isfile(INI_FILE)
    if file_check is False:
        return render_template("error.html", table='Group', data="", error=f'Luna Configuration File: <strong>{INI_FILE}</strong> Not Found')
    read_check = os.access(INI_FILE, os.R_OK)
    if read_check is False:
        return render_template("error.html", table='Group', data="", error=f'Luna Configuration File: <strong>{INI_FILE}</strong> is not readable.')
    return None


@app.errorhandler(404)
def page_not_found(e):
    """
    This method will redirect to error Template Page with Error Message on 404.
    Static assets must not return text/html (with a 200) or browsers show broken images.
    """
    try:
        p = request.path or ""
    except RuntimeError:
        p = ""
    if p.startswith("/app/assets/"):
        return "Not Found", 404, {"Content-Type": "text/plain; charset=utf-8"}
    return render_template("error.html", table='Group', data="", error=f"ERROR :: {e}"), 200


@app.route('/', methods=['GET'])
def home():
    """
    Serve the Vue SPA shell. window.APP_URL is this app's base URL.
    """
    url = Rest.app_url(request)
    # url = {"APP_URL": f"{request.scheme}://{request.host}{request.path}"}
    print(url)
    return render_template("index.html", APP_URL=url["APP_URL"])


@app.route('/api/v1/all_groups', methods=['GET'])
def all_groups():
    """
    Get a JSON list of all groups for the Vue frontend table.
    """
    response = Rest().get_data(TABLE)
    return response

@app.route('/api/v1/get_resources', methods=['GET'])
@app.route('/api/v1/get_resources/<string:record>', methods=['GET'])
def get_resources(record: str = ""):
    """
    Get a JSON list of all get_resources for the Vue frontend table.
    """
    body = {"bmcsetup_list": [],"osimage_list": [],"network_list": [],"bond_modes": []}
    if record:
        data = {"bmcsetupname": "", "osimage": "", "network": ""}
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        if "status" in table_data:
            if table_data["status"] is True:
                data = table_data["content"]["config"][TABLE][record]
            else:
                return jsonify(table_data)
        else:
            return jsonify(table_data)

        bmcsetup_list = Model().get_list_options_json('bmcsetup',  data.get("bmcsetupname"))
        osimage_list = Model().get_list_options_json('osimage', data.get("osimage"))
        network_list = Model().get_list_options_json('network')
        bond_modes = Helper().get_bond_mode_list()
        body = {
            "bmcsetup_list": bmcsetup_list,
            "osimage_list": osimage_list,
            "network_list": network_list,
            "bond_modes": bond_modes,
        }
    else:
        bmcsetup_list = Model().get_list_options_json('bmcsetup')
        osimage_list = Model().get_list_options_json('osimage')
        network_list = Model().get_list_options_json('network')
        bond_modes = Helper().get_bond_mode_list()
        body = {
            "bmcsetup_list": bmcsetup_list,
            "osimage_list": osimage_list,
            "network_list": network_list,
            "bond_modes": bond_modes,
        }
    return jsonify(body)


@app.route('/api/v1/group/<string:record>', methods=['GET'])
def group(record=None):
    """
    This Method will show a specific record.
    """
    response = Rest().get_data(TABLE, record)
    return response


@app.route('/api/v1/add', methods=['POST'])
def add():
    """
    This Method will add a requested record.
    """
    request_data, err = _group_write_payload()
    if err:
        return err

    name = next(iter(request_data["config"][TABLE]))
    response = Rest().post_data(TABLE, name, request_data)
    print(response)
    return jsonify(response), 200


@app.route('/api/v1/edit', methods=['POST'])
def edit():
    """
    This Method will add a requested record.
    """
    request_data, err = _group_write_payload()
    if err:
        return err

    name = next(iter(request_data["config"][TABLE]))
    response = Rest().post_data(TABLE, name, request_data)
    return jsonify(response), 200


@app.route('/rename/<string:record>', methods=['GET', 'POST'])
def rename(record=None):
    """
    This method will Rename the BMC Setup.
    """
    data = {}
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload['name'] = payload['name']
        payload['newgroupname'] = payload['newname']
        del payload['newname']
        response = Helper().update_record(TABLE, payload)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            flash(f'{TABLE_CAP} renamed to {payload["name"]}.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('rename', record=payload['newgroupname']), code=302)
    elif request.method == 'GET':
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        if table_data:
            raw_data = table_data['config'][TABLE][record]
            data = {'name': raw_data['name'], 'newname': ''}
    return render_template("rename.html", table=TABLE_CAP, data=data)


@app.route('/api/v1/delete/<string:record>', methods=['DELETE', 'GET'])
def delete(record: str=''):
    """
    This Method will delete a requested record.
    """
    response = Rest().get_delete(TABLE, record)
    LOGGER.info(response)
    return jsonify(response), 200


@app.route('/api/v1/remove-interface/<path:record>/<path:interface>', methods=['GET'])
@app.route('/remove/<path:record>/<path:interface>', methods=['GET'])
def remove_interface(record: str = '', interface: str = ''):
    """
    Remove a group interface via daemon GET _delete (same pattern as node app).
    """
    uri = f'{record}/interfaces/{interface}'
    response = Rest().get_delete(TABLE, uri)
    LOGGER.info(response)
    return jsonify(response), 200


@app.route('/api/v1/ospush/<string:record>', methods=['POST'])
def ospush(record: str=''):
    """
    This method will open the Login Page(First Page)
    """

    request_data = request.get_json()
    if not request_data:
        return jsonify({"status": False, "message": "No JSON payload received"}), 400
    uri = f'config/{TABLE}/{record}/_ospush'
    response = Rest().post_raw(uri, request_data)
    return response
    


@app.route('/api/v1/clone', methods=['POST'])
def clone():
    """
    This Method will add a requested record.
    """
    request_data, err = _group_write_payload()
    if err:
        return err

    name = next(iter(request_data["config"][TABLE]))
    response = Rest().post_clone(TABLE, name, request_data)
    return jsonify(response), 200


@app.route('/api/v1/status/<string:request_id>', methods=['GET'])
def check_status(request_id: str =""):
    """
    This method will check the status of request on behalf of request ID.
    """
    uri = f'config/status/{request_id}'
    response = Rest().get_raw(uri)
    print(response)
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
        _ssl_crt = '/trinity/local/etc/ssl/vmware-controller1.cluster.crt'
        _ssl_key = '/trinity/local/etc/ssl/vmware-controller1.cluster.key'
        if os.path.isfile(_ssl_crt) and os.path.isfile(_ssl_key):
            dev_context = (_ssl_crt, _ssl_key)
            app.run(host='0.0.0.0', port=7755, debug=True, ssl_context=dev_context)
        else:
            app.run(host='0.0.0.0', port=7755, debug=True)
    else:
        app.run()

# Run in Dev mode with TLS (read certs as the app user):
# sudo setfacl -m u:admin:r /trinity/local/etc/ssl/yixin3-dev-ctrl001.cluster.*
# sudo -u admin bash -c '. /trinity/local/python/bin/activate && python app.py'
