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
Luna 2 OS Image Tag — Flask shell + thin /api/v1 proxy to Luna daemon (same layout as node/group/osimage).
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
from model import Model

LOGGER = Log.init_log('INFO')
TABLE = 'osimagetag'
TABLE_CAP = 'OS Image Tag'

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
    if request.path.startswith('/app/assets/'):
        return None
    if isinstance(TOKEN_FILE, dict):
        return render_template("error.html", table=TABLE_CAP, data="", error=TOKEN_FILE["error"])
    if not os.path.isfile(INI_FILE):
        return render_template("error.html", table=TABLE_CAP, data="", error=f'Luna Configuration File: <strong>{INI_FILE}</strong> Not Found')
    if not os.access(INI_FILE, os.R_OK):
        return render_template("error.html", table=TABLE_CAP, data="", error=f'Luna Configuration File: <strong>{INI_FILE}</strong> is not readable.')
    return None


@app.errorhandler(404)
def page_not_found(e):
    """
    Static assets must not return text/html with 200 or browsers show broken images.
    """
    try:
        p = request.path or ""
    except RuntimeError:
        p = ""
    if p.startswith("/app/assets/"):
        return "Not Found", 404, {"Content-Type": "text/plain; charset=utf-8"}
    return render_template("error.html", table=TABLE_CAP, data="", error=f"ERROR :: {e}"), 200


@app.route('/', methods=['GET'])
def home():
    url = Rest.app_url(request)
    return render_template("index.html", APP_URL=url["APP_URL"])


@app.route('/api/v1/osimage', methods=['GET'])
def api_v1_osimage_list():
    """List OS images from daemon (same contract as trinityx-ood/osimage) for SPA pickers."""
    return jsonify(Rest().get_data('osimage'))


@app.route('/api/v1/osimagetag', methods=['GET'])
def api_v1_osimagetag_list():
    return jsonify(Rest().get_data(TABLE))


@app.route('/api/v1/osimagetag/<string:name>', methods=['GET'])
def api_v1_osimagetag_one(name):
    return jsonify(Rest().get_data(TABLE, name))


@app.route('/api/v1/osimage/<string:osimage>/tag', methods=['POST'])
def api_v1_osimage_tag_post(osimage):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"error": "Expected application/json body"}), 400
    request_data = body.get('request_data')
    if request_data is None:
        return jsonify({"error": "JSON must include 'request_data'"}), 400
    response = Rest().post_data("osimage", f"{osimage}/tag", request_data)
    LOGGER.info('%s %s', getattr(response, 'status_code', response), getattr(response, 'content', ''))
    return Rest.forward_daemon_response(response)


@app.route(
    '/api/v1/delete/osimage/<string:osimage>/osimagetag/<string:tag>',
    methods=['DELETE'],
)
def api_v1_delete_osimagetag(osimage, tag):
    response = Rest().get_delete("osimage", f'{osimage}/osimagetag/{tag}')
    LOGGER.info('%s %s', response.status_code, response.content)
    return Rest.forward_daemon_response(response)


@app.route('/api/v1/get_record/<string:record>', methods=['GET'])
def api_v1_get_record(record):
    return jsonify(Model().get_record(TABLE, record))


@app.route('/api/v1/license', methods=['GET'])
def api_v1_license():
    if os.path.isfile(LICENSE) and os.access(LICENSE, os.R_OK):
        with open(LICENSE, 'r', encoding="utf-8") as f:
            return jsonify({"license": f.read()})
    return jsonify({
        "license": None,
        "error": "LICENSE Information is not available at this moment.",
    })


if __name__ == "__main__":
    if APP_STATE is False:
        app.run(host='0.0.0.0', port=7755, debug=True)
    else:
        app.run()
