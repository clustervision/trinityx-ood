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
This File is a Main File Luna 2 OS Image.
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

# SPA: templates and error shell in app/; static assets in app/assets.
# Expose assets explicitly under /app/assets to avoid ambiguity with legacy /static paths.
app = Flask(
    __name__,
    static_folder="app/assets",
    static_url_path="/app/assets",
    template_folder="app",
)

TABLE = 'osimage'
TABLE_CAP = 'OS Image'

if APP_STATE is False:
    app.config["DEBUG"] = True
    os.environ["FLASK_ENV"] = "development"


def _chroot_base_url(req):
    """OOD shell URL base for lchroot links (environment only, not osimage data)."""
    if req.headers and "X-Forwarded-Proto" in dict(req.headers):
        scheme = dict(req.headers)["X-Forwarded-Proto"]
    else:
        scheme = req.scheme
    return f"{scheme}://{req.host}/pun/sys/shell/ssh/{req.host.split(':')[0]}"


def _require_json():
    data = request.get_json(silent=True)
    if data is None:
        return None
    return data


@app.before_request
def validate_home_directory():
    if request.path.startswith('/app/assets/'):
        return
    if isinstance(TOKEN_FILE, dict):
        return render_template("error.html", table=TABLE_CAP, data="", error=TOKEN_FILE["error"])
    if not os.path.isfile(INI_FILE):
        return render_template(
            "error.html",
            table=TABLE_CAP,
            data="",
            error=f'Luna Configuration File: <strong>{INI_FILE}</strong> Not Found',
        )
    if not os.access(INI_FILE, os.R_OK):
        return render_template(
            "error.html",
            table=TABLE_CAP,
            data="",
            error=f'Luna Configuration File: <strong>{INI_FILE}</strong> is not readable.',
        )
    return None


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": f"ERROR :: {e}"}), 404


@app.route('/', methods=['GET'])
def home():
    """Serve the Vue SPA shell. window.APP_URL is this app's base URL."""
    url = Rest.app_url(request)
    return render_template("index.html", APP_URL=url["APP_URL"])


@app.route('/api/v1/meta/chroot_base', methods=['GET'])
def api_v1_meta_chroot_base():
    return jsonify({"chroot_base_url": _chroot_base_url(request)})


@app.route('/api/v1/osimage', methods=['GET'])
def api_v1_osimage_list():
    return jsonify(Rest().get_data(TABLE))


@app.route('/api/v1/osimage/<string:name>', methods=['GET'])
def api_v1_osimage_one(name):
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
    """Client sends the same JSON that Rest.post_data expects (after TS prepare_payload)."""
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


@app.route('/api/v1/member/<string:table>/<string:record>', methods=['GET'])
def api_v1_member(table, record):
    return jsonify(Rest().get_data(table, record + '/_member'))


@app.route('/api/v1/kernel/<string:name>', methods=['GET'])
def api_v1_kernel_get(name):
    return jsonify(Rest().get_data(TABLE, name))


@app.route('/api/v1/kernel/<string:name>', methods=['POST'])
def api_v1_kernel_post(name):
    body = _require_json()
    if body is None:
        return jsonify({"error": "Expected application/json body"}), 400
    return Rest.forward_daemon_response(Rest().post_data(TABLE, f'{name}/kernel', body))


@app.route('/api/v1/request/<string:status>/<string:service_name>/<string:action>', methods=['GET'])
def api_v1_request(status, service_name, action):
    uri = f'{status}/{service_name}/{action}'
    if action == '_pack':
        uri = f'config/{uri}'
    return Rest.forward_daemon_response(Rest().get_raw(uri))


@app.route('/api/v1/check_status/<string:status>/status/<string:request_id>', methods=['GET'])
def api_v1_check_status(status, request_id):
    uri = f'{status}/status/{request_id}'
    resp = Rest().get_raw(uri)
    return Rest.forward_daemon_response(resp)


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
        _ssl_crt = '/trinity/local/etc/ssl/yixin3-dev-ctrl001.cluster.crt'
        _ssl_key = '/trinity/local/etc/ssl/yixin3-dev-ctrl001.cluster.key'
        if os.path.isfile(_ssl_crt) and os.path.isfile(_ssl_key):
            dev_context = (_ssl_crt, _ssl_key)
            app.run(host='0.0.0.0', port=7755, debug=True, ssl_context=dev_context)
        else:
            app.run(host='0.0.0.0', port=7755, debug=True)
    else:
        app.run()
