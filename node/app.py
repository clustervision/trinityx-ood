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
Luna2 Nodes Main Flask Application.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2026, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Production'


import os
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from rest import Rest
from constant import LICENSE, INI_FILE, TOKEN_FILE, APP_STATE
from log import Log

LOGGER = Log.init_log('INFO')
TABLE = "node"
TABLE_CAP = "Node"
API_VERSION = "v1"

app = Flask(__name__, static_folder="app/assets", static_url_path="/app/assets", template_folder="app")

if APP_STATE is False:
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})


def relay_requests_response(resp):
    """
    requests.Response → Flask (JSON body + status).
    """
    if resp is False or resp is None:
        return jsonify({"message": "No response from daemon"}), 502
    try:
        body = resp.json()
    except ValueError:
        body = {"message": (resp.text or "")[:8192]}
    return jsonify(body), resp.status_code


def single_node_config_bundle(req_json):
    """
    Expect {"config": {TABLE: {<name>: <recorddict>}}} with exactly one name key.
    Returns (name str, bundle dict).
    """
    cfg = req_json.get('config')
    if not isinstance(cfg, dict):
        raise ValueError("body must contain object 'config'")
    tab = cfg.get(TABLE)
    if not isinstance(tab, dict) or len(tab) != 1:
        raise ValueError(f"config.{TABLE} must be an object with exactly one node name key")
    name, record = next(iter(tab.items()))
    if not isinstance(name, str) or not name:
        raise ValueError("invalid node name")
    return name, req_json


def relay_node_write(body, rest_fn):
    """
    Parse {config:...} or {name, record}, call rest_fn(name, bundle)->requests.Response.
    """
    if not isinstance(body, dict):
        return jsonify({"error": "JSON body required"}), 400
    try:
        if 'config' in body:
            name, bundle = single_node_config_bundle(body)
            return relay_requests_response(rest_fn(name, bundle))
        if 'name' in body and 'record' in body and isinstance(body['record'], dict):
            bundle = {'config': {TABLE: {body['name']: body['record']}}}
            return relay_requests_response(rest_fn(body['name'], bundle))
    except ValueError as ex:
        return jsonify({"error": str(ex)}), 400
    return jsonify({"error": "expected {config:...} or {name, record}"}), 400


@app.before_request
def validate_home_directory():
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
    return render_template("error.html", table=TABLE_CAP, data="", error=f"ERROR :: {e}"), 200


@app.route('/', methods=["GET"])
def home():
    """
    This method will open the main page of the application.
    """
    url = Rest().app_url(request)
    LOGGER.info(f"{TABLE_CAP} :: Home URL: {url}")
    return render_template("index.html", APP_URL=url["APP_URL"])


@app.route(f"/api/{API_VERSION}/node", methods=["GET"])
@app.route(f"/api/{API_VERSION}/node/<string:node_name>", methods=["GET"])
def get_nodes(node_name: str = ""):
    """
    Get all nodes or requested node from the Luna daemon.
    """
    response = {"status": False, "status_code": 500, "content": ""}
    if node_name:
        response = Rest().get_data(table = TABLE, name = node_name)
    else:
        response = Rest().get_data(table = TABLE)
    LOGGER.info(f"{TABLE_CAP} :: Node Response: {response}")
    return response


@app.route(f"/api/{API_VERSION}/resource/<string:resource_name>", methods=["GET"])
def get_resource(resource_name: str = ""):
    """
    This route will fetch all the records from the Luna Daemon for the requested resource.
    """
    LOGGER.info(f"{TABLE_CAP} :: Resource Response: {resource_name}")
    return Rest().get_data(table = resource_name)


@app.route(f"/api/{API_VERSION}/table/<string:table>/<path:uri>", methods=["GET"])
def get_table_named(table, uri):
    """
    GET config/<table>/<uri...> passthrough.
    """
    LOGGER.info(f"{TABLE_CAP} :: Table Response: {table}/{uri}")
    return Rest().get_data(table, uri)



@app.route(f"/api/{API_VERSION}/add", methods=["POST"])
def api_add():
    """
    POST {"config":{"node":{"<name>":{...}}}} or {"name":"<node>","record":{...}}.
    Creates / posts to Luna (same as daemon POST /config/node/<name>).
    """
    return relay_node_write(request.get_json(silent=True), lambda n, b: Rest().post_data(TABLE, n, b))


@app.route(f"/api/{API_VERSION}/update/<path:name>", methods=["POST"])
def api_update(name):
    """
    POST JSON = node fields object; wraps config.node[name] for Luna POST.
    """
    rec = request.get_json(silent=True)
    if not isinstance(rec, dict):
        return jsonify({"error": "JSON body (record object) required"}), 400
    bundle = {'config': {TABLE: {name: rec}}}
    return relay_requests_response(Rest().post_data(TABLE, name, bundle))


@app.route(f"/api/{API_VERSION}/rename", methods=["POST"])
def api_rename():
    """
    Same POST shape as /api/{API_VERSION}/add; client puts rename fields (e.g. newnodename) in record."""
    return relay_node_write(request.get_json(silent=True), lambda n, b: Rest().post_data(TABLE, n, b))


@app.route(f"/api/{API_VERSION}/delete/<path:name>", methods=['DELETE'])
def api_delete(name):
    return Rest().get_delete(TABLE, name)


@app.route(f"/api/{API_VERSION}/remove-interface/<path:record>/<path:interface>", methods=['DELETE', 'GET'])
@app.route(f"/api/{API_VERSION}/remove/<path:record>/<path:interface>", methods=["GET"])
def api_remove_interface(record, interface):
    """
    DELETE / GET — match legacy Luna _delete URL pattern.
    """
    uri = f'{record}/interfaces/{interface}'
    resp = Rest().get_delete(TABLE, uri)
    LOGGER.info(resp)
    return jsonify(resp), 200


@app.route(f"/api/{API_VERSION}/clone", methods=["POST"])
def api_clone():
    """
    POST {"config":{"node":{"<newname>":{...}}}} or {"name":"<new>","record":{...}}.
    """
    return relay_node_write(request.get_json(silent=True), lambda n, b: Rest().post_clone(TABLE, n, b))


@app.route(f"/api/{API_VERSION}/osgrab/<path:name>", methods=["POST"])
def api_osgrab(name):
    rec = request.get_json(silent=True)
    if not isinstance(rec, dict):
        rec = {}
    bundle = {'config': {TABLE: {name: rec}}}
    uri = f'config/{TABLE}/{name}/_osgrab'
    return relay_requests_response(Rest().post_raw(uri, bundle))


@app.route(f"/api/{API_VERSION}/ospush/<path:name>", methods=["POST"])
def api_ospush(name):
    rec = request.get_json(silent=True)
    if not isinstance(rec, dict):
        rec = {}
    bundle = {'config': {TABLE: {name: rec}}}
    uri = f'config/{TABLE}/{name}/_ospush'
    return relay_requests_response(Rest().post_raw(uri, bundle))


@app.route(f"/api/{API_VERSION}/check_status/<string:status_seg>/status/<string:request_id>", methods=["GET"])
def api_check_status(status_seg, request_id):
    uri = f'{status_seg}/status/{request_id}'
    result = Rest().get_raw(uri)
    if not result:
        return jsonify({"message": "No response from daemon", "status_code": None}), 502
    try:
        body = result.json()
    except ValueError:
        text = (result.text or "").strip()
        return jsonify({"message": "Daemon returned non-JSON body", "status_code": result.status_code, "body": text, }), 200 if result.ok else result.status_code
    return jsonify(body), result.status_code


@app.route(f"/api/{API_VERSION}/license", methods=["GET"])
def license_info():
    response = 'LICENSE Information is not available at this moment.'
    if os.path.isfile(LICENSE) and os.access(LICENSE, os.R_OK):
        with open(LICENSE, 'r', encoding="utf-8") as file_data:
            response = '<br />'.join(file_data.readlines())
    return response


if __name__ == "__main__":
    if APP_STATE is False:
        app.run(host='0.0.0.0', port=7755, debug=True)
    else:
        app.run()
