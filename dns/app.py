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
Luna 2 DNS — Flask shell + /api/v1 proxy for Vue SPA frontend.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

import os
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from rest import Rest
from constant import LICENSE, INI_FILE, TOKEN_FILE, APP_STATE
from log import Log
from model import Model

LOGGER = Log.init_log('INFO')
TABLE = 'dns'
TABLE_CAP = 'DNS'
app = Flask(
    __name__,
    static_folder="app/assets",
    static_url_path="/app/assets",
    template_folder="app",
)

if APP_STATE is False:
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
    app.config["DEBUG"] = True
    os.environ["FLASK_ENV"] = "development"


@app.before_request
def validate_home_directory():
    """
    Validate the $HOME directory of the user before proceeding further.
    """
    if request.path.startswith('/app/assets/'):
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
    Serve Vue SPA shell.
    """
    root_path = request.script_root if request.script_root else request.path
    app_url = f"{request.scheme}://{request.host}{root_path}"
    return render_template("index.html", APP_URL=app_url)


@app.route('/api/v1/networks', methods=['GET'])
def networks():
    """
    Return network names used by DNS form dropdown.
    """
    names = Model().get_name_list('network')
    return jsonify({"networks": names}), 200


@app.route('/api/v1/dns_entries', methods=['GET'])
def dns_entries():
    """
    Return flattened DNS list: [{network, host, ipaddress}, ...].
    """
    entries = []
    networks = Model().get_name_list('network')
    for network in networks:
        dns_data = Rest().get_data(TABLE, network)
        if not isinstance(dns_data, dict):
            continue
        rows = (
            dns_data.get("config", {})
            .get(TABLE, {})
            .get(network, [])
        )
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict):
                    entries.append({
                        "network": network,
                        "host": row.get("host", ""),
                        "ipaddress": row.get("ipaddress", ""),
                    })
    return jsonify({"entries": entries}), 200


@app.route('/api/v1/dns/<string:network>', methods=['POST'])
def add_or_update_dns(network: str):
    """
    Add/update one DNS host entry for the given network.
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"message": "No JSON payload received"}), 400

    host = str(payload.get("host", "")).strip()
    ipaddress = str(payload.get("ipaddress", "")).strip()
    if not network or not host or not ipaddress:
        return jsonify({"message": "network, host and ipaddress are required"}), 400

    request_data = {
        "config": {
            TABLE: {
                network: [{"host": host, "ipaddress": ipaddress}]
            }
        }
    }
    response = Rest().post_data(TABLE, network, request_data)
    if not response:
        return jsonify({"message": "No response from daemon"}), 502
    try:
        body = response.json()
    except ValueError:
        body = {"message": (response.text or "")[:8192]}
    if response.status_code in (201, 204):
        return jsonify({"status": True, "content": body}), 200
    return jsonify(body), response.status_code


@app.route('/api/v1/dns/<string:network>/<string:host>', methods=['DELETE'])
def delete_dns(network: str, host: str):
    """
    Delete one DNS host from the given network.
    """
    response = Rest().get_delete(TABLE, f"{network}/{host}")
    if not response:
        return jsonify({"message": "No response from daemon"}), 502
    if response.status_code == 204:
        return jsonify({"status": True, "content": {"message": "deleted"}}), 204
    try:
        body = response.json()
    except ValueError:
        body = {"message": (response.text or "")[:8192]}
    return jsonify(body), response.status_code


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
        app.run(host='0.0.0.0', port=7755, debug=True)
    else:
        app.run()
