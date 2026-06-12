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

"""Control SPA shell + API relay for Luna daemon."""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

import os
from flask import Flask, jsonify, request, render_template
from rest import Rest
from constant import LICENSE, INI_FILE, TOKEN_FILE, APP_STATE
from helper import Helper
from log import Log

LOGGER = Log.init_log('INFO')
TABLE = 'control'
TABLE_CAP = 'Control Nodes'
app = Flask(
    __name__,
    static_folder="app/assets",
    static_url_path="/app/assets",
    template_folder="app",
)

if APP_STATE is False:
    app.config["DEBUG"] = True
    os.environ["FLASK_ENV"] = "development"


@app.before_request
def validate_home_directory():
    """
    Validate the $HOME directory of the user before proceeding further.
    """
    if request.path.startswith('/app/assets/'):
        return None
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
    try:
        p = request.path or ""
    except RuntimeError:
        p = ""
    if p.startswith("/app/assets/"):
        return "Not Found", 404, {"Content-Type": "text/plain; charset=utf-8"}
    return render_template("error.html", table="Control Nodes", data="", error=f"ERROR :: {e}"), 200


@app.route('/', methods=['GET'])
def home():
    url = Rest().app_url(request)
    return render_template("index.html", APP_URL=url["APP_URL"])


def _status_node_list():
    """Resolve node names for status queries (optional subset via GET query or POST body)."""
    node_list = []
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        raw = data.get('hostlist') or data.get('nodes') or []
        if isinstance(raw, list):
            node_list = [str(n).strip() for n in raw if str(n).strip()]
        elif isinstance(raw, str) and raw.strip():
            node_list = [n.strip() for n in raw.split(',') if n.strip()]
    else:
        raw = request.args.get('hostlist') or request.args.get('nodes') or ''
        if raw:
            node_list = [n.strip() for n in raw.split(',') if n.strip()]
    if not node_list:
        node_list = Helper().get_name_list('node')
    return node_list


@app.route('/api/v1/get_nodes', methods=['GET'])
def get_nodes():
    """
    Return all node names for the Vue table without querying per-node status.
    """
    node_list = Helper().get_name_list('node')
    return jsonify({'node_list': node_list}), 200


@app.route('/api/v1/status', methods=['GET', 'POST'])
def get_status():
    node_list = _status_node_list()
    if not node_list:
        return jsonify({'results': [], 'request_ids': {'power': '', 'sel': '', 'chassis': ''}, 'nodes': []}), 200
    hostlist = Helper().collect_nodelist(node_list)
    systems = {'power': 'status', 'sel': 'list', 'chassis': 'identify'}
    results = []
    request_ids = {'power': '', 'sel': '', 'chassis': ''}

    for system, action in systems.items():
        payload = {'control': {system: {action: {"hostlist": hostlist}}}}
        uri = f'control/action/{system}/_{action}'
        result = Rest().post_raw(uri, payload)
        if result is False:
            continue
        body = result.json()
        results.append(body)
        request_ids[system] = str(body.get('request_id', ''))
    return jsonify({'results': results, 'request_ids': request_ids, 'nodes': node_list})


@app.route('/api/v1/action/<string:system>/<string:action>', methods=['POST'])
def perform(system=None, action=None):
    request_data = request.get_json(silent=True) or {}
    hostlist = request_data.get('hostlist', [])
    hostlist = Helper().collect_nodelist(hostlist)
    payload = {'control': {system: {action: {"hostlist": hostlist}}}}
    uri = f'control/action/{system}/_{action}'
    result = Rest().post_raw(uri, payload)
    if result is False:
        return jsonify({"message": "No response from daemon"}), 502
    return jsonify(result.json()), result.status_code


@app.route('/api/v1/request/<string:request_id>', methods=['GET'])
def check_request(request_id=None):
    uri = f'control/status/{request_id}'
    result = Rest().get_raw(uri)
    if result is False:
        return jsonify({"message": "No response from daemon"}), 502
    LOGGER.info('%s %s', result.status_code, result.content)
    return jsonify(result.json()), result.status_code


@app.route('/api/v1/license', methods=['GET'])
def license_info():
    response = 'LICENSE Information is not available at this moment.'
    file_check = os.path.isfile(LICENSE)
    read_check = os.access(LICENSE, os.R_OK)
    if file_check and read_check:
        with open(LICENSE, 'r', encoding="utf-8") as file_data:
            response = file_data.read()
    return jsonify({"license": response})


if __name__ == "__main__":
    if APP_STATE is False: 
        app.run(host='0.0.0.0', port=7755, debug=True)
    else:
        app.run()
