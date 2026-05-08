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
This File is a Main File Luna 2 OS Image Tag.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

import os
from flask import Flask, jsonify, render_template, request
from rest import Rest
from constant import LICENSE, INI_FILE, TOKEN_FILE, APP_STATE
from log import Log

app = Flask(
    __name__,
    static_folder="app/assets",
    static_url_path="/app/assets",
    template_folder="app",
)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

LOGGER = Log.init_log('INFO')
TABLE = 'osimagetag'
TABLE_CAP = 'OS Image Tag'

if APP_STATE is False:
    app.config["DEBUG"] = True
    os.environ["FLASK_ENV"] = "development"


def _require_json():
    data = request.get_json(silent=True)
    if data is None:
        return None
    return data


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
    return jsonify({"error": f"ERROR :: {e}"}), 404


@app.route('/', methods=['GET'])
def home():
    """Serve the Vue SPA shell."""
    url = Rest.app_url(request)
    return render_template("index.html", APP_URL=url["APP_URL"])


@app.route('/api/v1/osimagetag', methods=['GET'])
def api_v1_osimagetag_list():
    return jsonify(Rest().get_data(TABLE))


@app.route('/api/v1/osimagetag/<string:name>', methods=['GET'])
def api_v1_osimagetag_one(name):
    return jsonify(Rest().get_data(TABLE, name))


@app.route('/api/v1/add', methods=['POST'])
def api_v1_add():
    body = _require_json()
    if body is None:
        return jsonify({"error": "Expected application/json body"}), 400
    rec_name = body.get('name')
    request_data = body.get('request_data')
    if not rec_name or request_data is None:
        return jsonify({"error": "JSON must include 'name' and 'request_data'"}), 400
    return Rest.forward_daemon_response(Rest().post_data(TABLE, rec_name, request_data))


@app.route('/api/v1/edit', methods=['POST'])
def api_v1_edit():
    body = _require_json()
    if body is None:
        return jsonify({"error": "Expected application/json body"}), 400
    rec_name = body.get('name')
    request_data = body.get('request_data')
    if not rec_name or request_data is None:
        return jsonify({"error": "JSON must include 'name' and 'request_data'"}), 400
    return Rest.forward_daemon_response(Rest().post_data(TABLE, rec_name, request_data))


@app.route('/api/v1/rename', methods=['POST'])
def api_v1_rename():
    body = _require_json()
    if body is None:
        return jsonify({"error": "Expected application/json body"}), 400
    rec_name = body.get('name')
    request_data = body.get('request_data')
    if not rec_name or request_data is None:
        return jsonify({"error": "JSON must include 'name' and 'request_data'"}), 400
    return Rest.forward_daemon_response(Rest().post_data(TABLE, rec_name, request_data))


@app.route('/api/v1/delete/<string:name>', methods=['DELETE'])
def api_v1_delete(name):
    return Rest.forward_daemon_response(Rest().get_delete(TABLE, name))


@app.route('/api/v1/delete/osimage/<string:osimage>/osimagetag/<string:tag>', methods=['DELETE'])
def api_v1_delete_tag(osimage, tag):
    return Rest.forward_daemon_response(Rest().get_delete("osimage", f'{osimage}/osimagetag/{tag}'))


@app.route('/api/v1/clone', methods=['POST'])
def api_v1_clone():
    body = _require_json()
    if body is None:
        return jsonify({"error": "Expected application/json body"}), 400
    source = body.get('source_name')
    request_data = body.get('request_data')
    if not source or request_data is None:
        return jsonify({"error": "JSON must include 'source_name' and 'request_data'"}), 400
    return Rest.forward_daemon_response(Rest().post_clone(TABLE, source, request_data))


@app.route('/api/v1/osimage/<string:osimage>/tag', methods=['POST'])
def api_v1_add_tag(osimage):
    body = _require_json()
    if body is None:
        return jsonify({"error": "Expected application/json body"}), 400
    request_data = body.get('request_data')
    if request_data is None:
        return jsonify({"error": "JSON must include 'request_data'"}), 400
    return Rest.forward_daemon_response(Rest().post_data("osimage", f"{osimage}/tag", request_data))


@app.route('/api/v1/member/<string:table>/<string:record>', methods=['GET'])
def api_v1_member(table, record):
    return jsonify(Rest().get_data(table, record + '/_member'))


@app.route('/api/v1/request/<string:status>/<string:service_name>/<string:action>', methods=['GET'])
def api_v1_request(status, service_name, action):
    uri = f'{status}/{service_name}/{action}'
    if action == '_pack':
        uri = f'config/{uri}'
    return Rest.forward_daemon_response(Rest().get_raw(uri))


@app.route('/api/v1/check_status/<string:status>/status/<string:request_id>', methods=['GET'])
def api_v1_check_status(status, request_id):
    uri = f'{status}/status/{request_id}'
    return Rest.forward_daemon_response(Rest().get_raw(uri))


@app.route('/api/v1/license', methods=['GET'])
def api_v1_license():
    file_check = os.path.isfile(LICENSE)
    read_check = os.access(LICENSE, os.R_OK)
    if file_check and read_check:
        with open(LICENSE, 'r', encoding="utf-8") as file_data:
            content = file_data.read()
        return jsonify({"license": content})
    return jsonify({"license": None, "error": "LICENSE Information is not available at this moment."})


if __name__ == "__main__":
    if APP_STATE is False:
        app.run(host='0.0.0.0', port=7755, debug=True)
    else:
        app.run()
