#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This code is part of the TrinityX software suite
# Copyright (C) 2026  ClusterVision Solutions b.v.
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
This File is a Main File Luna 2 Other Device.
This file will create flask object and serve the all routes for on demand.
"""

__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2026, Luna2 Project [OOD]"
__license__     = "GPL"
__version__     = "3.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Production"


import os
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from rest import Rest
from constant import LICENSE, INI_FILE, TOKEN_FILE, APP_STATE
from log import Log
from model import Model


LOGGER = Log.init_log('INFO')
TABLE = 'otherdev'
TABLE_CAP = 'Other Device'
API_VERSION = 'v1'

app = Flask(__name__, static_folder="app/assets", static_url_path="/app/assets", template_folder="app")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


if APP_STATE is False:
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
    app.config["DEBUG"] = True
    os.environ["FLASK_ENV"] = "development"


@app.route(f"/api/{API_VERSION}/routes", methods=['GET'])
def routes():
    """
    This method provide all the available routes in the application with method and function name.
    """
    response = []
    for rule in app.url_map.iter_rules():
        method = str(rule.methods).replace("'", "")
        method = method.replace("}", "")
        method = method.replace("{", "")
        method = method.replace("HEAD", "")
        method = method.replace("OPTIONS", "")
        method = method.replace(", ", "")
        route = f"https://{request.environ['HTTP_HOST']}{rule}"
        if "static" != str(rule.endpoint):
            response.append({"route": route, "function": str(rule.endpoint), "method": method})
    LOGGER.debug(response)
    return jsonify(response), 200


@app.before_request
def validate_home_directory():
    """
    Validate the $HOME directory of the user before proceeding further.
    """
    if request.path.startswith('/static/'):
        return
    if isinstance(TOKEN_FILE, dict):
        return render_template("error.html", table=TABLE_CAP, data="", error=TOKEN_FILE["error"])
    file_check = os.path.isfile(INI_FILE)
    if file_check is False:
        return render_template("error.html", table=TABLE_CAP, data="", error=f'Luna Configuration File: <strong>{INI_FILE}</strong> Not Found')
    read_check = os.access(INI_FILE, os.R_OK)
    if read_check is False:
        return render_template("error.html", table=TABLE_CAP, data="", error=f'Luna Configuration File: <strong>{INI_FILE}</strong> is not readable.')
    return None


@app.errorhandler(404)
def page_not_found(e):
    """
    This method will redirect to error Template Page with Error Message on 404.
    """
    return render_template("error.html", table=TABLE_CAP, data="", error=f"ERROR :: {e}"), 200


@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application. It will list all Other Device which is available with daemon.
    """
    url = Rest().app_url(request)
    LOGGER.debug(url)
    return render_template("index.html", APP_URL=url["APP_URL"])


@app.route(f"/api/{API_VERSION}/otherdevs", methods=['GET'])
def otherdevs():
    """
    This API will return all the Other Devices which is available with daemon.
    """
    response = Rest().get_data(TABLE)
    LOGGER.debug(response)
    return jsonify(response), 200


@app.route(f"/api/{API_VERSION}/add", methods=['POST'])
def add_record():
    """
    This Method will add a requested record.
    """
    request_data = request.get_json()
    if not request_data:
        return jsonify({"status": False, "status_code": 400, "message": "No JSON payload received"}), 400

    name = next(iter(request_data["config"][TABLE]))
    response = Rest().post_data(TABLE, name, request_data, action="add")
    LOGGER.debug(response)
    return jsonify(response), 200


@app.route(f"/api/{API_VERSION}/update", methods=['PUT'])
def update_record():
    """
    This Method will update a requested record.
    """
    request_data = request.get_json()
    if not request_data:
        return jsonify({"status": False, "status_code": 400, "message": "No JSON payload received"}), 400

    name = next(iter(request_data["config"][TABLE]))
    response = Rest().post_data(TABLE, name, request_data, action="update")
    LOGGER.debug(response)
    return jsonify(response), 200


@app.route(f"/api/{API_VERSION}/clone", methods=['POST'])
def clone_record():
    """
    This Method will clone a requested record.
    """
    request_data = request.get_json()
    if not request_data:
        return jsonify({"status": False, "status_code": 400, "message": "No JSON payload received"}), 400

    name = next(iter(request_data["config"][TABLE]))
    response = Rest().post_data(TABLE, name, request_data, action="clone")
    LOGGER.debug(response)
    return jsonify(response), 200


@app.route(f"/api/{API_VERSION}/rename", methods=['PATCH'])
def rename_record():
    """
    This method will rename the requested record.
    """
    request_data = request.get_json()
    if not request_data:
        return jsonify({"status": False, "message": "No JSON payload received"}), 400

    record = next(iter(request_data["config"][TABLE]))
    newname = request_data["config"][TABLE][record].get("newotherdevname", "")
    if record and newname:
        response = Rest().post_data(TABLE, record, request_data, action="rename")
        LOGGER.debug(response)
        return jsonify(response), 200
    else:
        return jsonify({"status": False, "status_code": 400, "content": "ERROR :: Record name and new name must be provided."}), 400


@app.route(f"/api/{API_VERSION}/delete/<string:record>", methods=['DELETE'])
def delete_record(record: str):
    """
    This Method will delete a requested record.
    """
    response = Rest().get_delete(TABLE, record)
    LOGGER.info(response)
    return jsonify(response), 200


@app.route('/api/v1/get_networks', methods=['GET'])
@app.route('/api/v1/get_networks/<string:record>', methods=['GET'])
def get_networks(record: str = ""):
    """
    Get a JSON list of all get_networks for the Vue frontend table.
    """
    body = {"network_list": []}
    if record:
        data = {"network": ""}
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        if "status" in table_data:
            if table_data["status"] is True:
                data = table_data["content"]["config"][TABLE][record]
            else:
                return jsonify(table_data)
        else:
            return jsonify(table_data)

        network_list = Model().get_list_options_json('network', data.get("network"))
        body = {"network_list": network_list}
    else:
        network_list = Model().get_list_options_json('network')
        body = {"network_list": network_list}
    return jsonify(body), 200


@app.route(f"/api/{API_VERSION}/license", methods=['GET'])
def license_info():
    """
    This Method will provide license in details.
    """
    response = 'LICENSE Information is not available at this moment.'
    file_check = os.path.isfile(LICENSE)
    read_check = os.access(LICENSE, os.R_OK)
    if file_check and read_check:
        with open(LICENSE, 'r', encoding="utf-8") as file_data:
            response = file_data.readlines()
            response = '<br />'.join(response)
    return response


if __name__ == "__main__":
    if APP_STATE is False:
        CRT = '/trinity/local/etc/ssl/vmware-controller1.cluster.crt'
        KEY = '/trinity/local/etc/ssl/vmware-controller1.cluster.key'
        if os.path.isfile(CRT) and os.path.isfile(KEY):
            dev_context = (CRT, KEY)
            app.run(host='0.0.0.0', port=7755, debug=True, ssl_context=dev_context)
        else:
            app.run(host='0.0.0.0', port=7755, debug=True)
    else:
        app.run()
