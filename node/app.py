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
This File is a Main File Luna 2 Node.
Flask API + Vue SPA (templates/index.html, static/spa/ from frontend build).
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'


import os
import json
from copy import deepcopy
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from rest import Rest
from constant import LICENSE, INI_FILE, TOKEN_FILE, APP_STATE
from helper import Helper
from log import Log
from model import Model

LOGGER = Log.init_log('INFO')
TABLE = 'node'
TABLE_CAP = 'Node'
# SPA: one Jinja shell in templates/index.html; Vue build output in static/spa/.
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

if APP_STATE is False:
    app.config["DEBUG"] = True
    os.environ["FLASK_ENV"] = "development"
    CORS(app, resources={r"/*": {"origins": "http://localhost:5174"}})


def _wants_json():
    """
    API clients: ?format=json or Accept prefers application/json.
    Browser navigation: default HTML — return SPA shell from GET handlers.
    """
    fmt = (request.args.get('format') or '').lower()
    if fmt == 'json':
        return True
    if fmt == 'html':
        return False
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'], 'text/html')
    return best == 'application/json'


def _next_free_ip(network):
    if not network:
        return None
    uri = f'{network}/_nextfreeip'
    nextip = Rest().get_data('network', uri)
    if nextip:
        return nextip['config']['network'][network].get('nextip')
    return None


def _node_os_bmc_sources(data):
    if not data:
        return None, None
    bmc_src = data.get('bmcsetup_source') or data.get('_bmcsetup_source')
    os_src = data.get('osimage_source') or data.get('_osimage_source')
    return bmc_src, os_src


def _nodes_inventory_json():
    """
    Same data the legacy GET / inventory page showed, as JSON for the Vue table.
    """
    empty = {"fields": [], "nodes": [], "error": ""}
    try:
        table_data = Rest().get_data(TABLE)
        LOGGER.info(table_data)
        if not table_data:
            empty["error"] = f'No {TABLE_CAP} Available at this time.'
            return jsonify(empty)
        if not isinstance(table_data, dict) or 'config' not in table_data:
            empty["error"] = 'Daemon returned an unexpected JSON shape (missing config).'
            return jsonify(empty)
        raw_data = table_data['config'].get(TABLE)
        if raw_data is None:
            empty["error"] = f'No {TABLE_CAP} key in daemon config.'
            return jsonify(empty)
        if not isinstance(raw_data, dict):
            empty["error"] = 'Node data from daemon is not a mapping; check Luna daemon response.'
            return jsonify(empty)
        raw_data = Helper().prepare_json(raw_data, True)
        fields, nodes = Helper().filter_data_json(TABLE, raw_data)
        return jsonify({"fields": fields, "nodes": nodes, "error": ""})
    except Exception as exc:
        LOGGER.exception("nodes inventory JSON failed")
        return jsonify({
            "fields": [],
            "nodes": [],
            "error": f'nodes inventory: {exc}',
        })


@app.before_request
def validate_home_directory():
    """
    Validate the $HOME directory of the user before proceeding further.
    JSON inventory (GET /?format=json) returns 200 + {fields,nodes,error} for the Vue table.
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
    return jsonify({"error": f"ERROR :: {e}"}), 404


@app.route('/', methods=['GET'])
def home():
    """
    Legacy URL: GET / was the node inventory page.
    - Browser (HTML): Vue SPA shell.
    - ?format=json or Accept: application/json: same inventory as JSON for the SPA table.
    """
    if _wants_json():
        return _nodes_inventory_json()
    app_url = Helper().node_app_base_url(request)
    context_url = Helper().context_url(request)
    return render_template(
        "index.html",
        APP_URL=app_url,
        CONTEXT_URL=context_url,
    )


@app.route('/show/<string:record>', methods=['GET'])
def show(record=None):
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config'][TABLE][record]
        raw_data = Helper().prepare_json(raw_data)
        node = Helper().filter_data_col_json(TABLE, raw_data)
        return jsonify({"node": node, "error": ""})
    return jsonify({"node": {}, "error": f'{record} From {TABLE_CAP} is Not available at this time'})


@app.route('/get_list/<string:table>', methods=['GET', 'POST'])
def get_list(table=None):
    if request:
        response = Model().get_list_options(table)
        return jsonify(response)
    return jsonify([])


@app.route('/nextip_network/<string:network>', methods=['GET'])
def nextip_network(network=None):
    nip = _next_free_ip(network)
    return jsonify({"nextip": nip})


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload["service"] = True if 'service' in payload else False
        payload["setupbmc"] = True if 'setupbmc' in payload else False
        payload["netboot"] = True if 'netboot' in payload else False
        payload["bootmenu"] = True if 'bootmenu' in payload else False
        table_data = Rest().get_data(TABLE, payload['name'])
        if table_data:
            if payload['name'] in table_data['config'][TABLE]:
                return jsonify({"message": f'{payload["name"]} is already present in the database.', "status": "error"}), 409
        payload = Helper().prepare_payload(None, payload)
        for k, v in list(payload.items()):
            if v == 'on':
                payload[k] = True
        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, TABLE, payload)
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_data(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 201:
            return jsonify({"message": f'{TABLE_CAP}, {payload["name"]} Created.', "status": "success"}), 201
        response_json = response.json()
        return jsonify({"message": f'{response.status_code} - {response_json["message"]}', "status": "error"}), response.status_code
    if not _wants_json():
        return home()
    return jsonify({
        "table": TABLE_CAP,
        "group_list": Model().get_list_options_json('group'),
        "bmcsetup_list": Model().get_list_options_json('bmcsetup'),
        "switch_list": Model().get_list_options_json('switch'),
        "osimage_list": Model().get_list_options_json('osimage'),
        "network_list": Model().get_list_options_json('network'),
        "bond_modes": Helper().get_bond_mode_list(),
    })


@app.route('/rename/<string:record>', methods=['GET', 'POST'])
def rename(record=None):
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload['name'] = payload['name']
        payload['newnodename'] = payload['newname']
        del payload['newname']
        response = Helper().update_record(TABLE, payload)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            return jsonify({"message": f'{TABLE_CAP} renamed to {payload["newnodename"]}.', "status": "success"}), 204
        response_json = response.json()
        return jsonify({"message": f'{response.status_code} - {response_json["message"]}', "status": "error"}), response.status_code
    if not _wants_json():
        return home()
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config'][TABLE][record]
        data = {'name': raw_data['name'], 'newname': ''}
        return jsonify({"data": data, "error": ""})
    return jsonify({"data": {}, "error": f'{record} not found.'}), 404


@app.route('/edit/<string:record>', methods=['GET', 'POST'])
def edit(record=None):
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None]}
        payload = Helper().prepare_payload(None, payload)
        payload["service"] = True if 'service' in payload else False

        osimage = payload.get('osimage') or ''
        if '(group)' in osimage:
            payload['osimage'] = ''
        elif '(' in osimage and ')' in osimage:
            payload['osimage'] = osimage.split('(', 1)[0]

        bmcsetup = payload.get('bmcsetup') or ''
        if '(group)' in bmcsetup:
            payload['bmcsetup'] = ''
        elif '(' in bmcsetup and ')' in bmcsetup:
            payload['bmcsetup'] = bmcsetup.split('(', 1)[0]

        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, TABLE, payload)
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_data(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            return jsonify({"message": f'{TABLE_CAP}, {payload["name"]} Updated.', "status": "success"}), 204
        if response.status_code == 201:
            response_json = response.json()
            return jsonify({"message": f'{TABLE_CAP} {response_json["message"]}.', "status": "success"}), 201
        response_json = response.json()
        return jsonify({"message": f'{response.status_code} - {response_json["message"]}', "status": "error"}), response.status_code

    if not _wants_json():
        return home()
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if not table_data:
        return jsonify({"data": {}, "record": record, "error": f'{record} not found.'}), 404
    data = table_data['config'][TABLE][record]
    data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
    data = Helper().prepare_json(data)
    bmc_src, os_src = _node_os_bmc_sources(data)
    return jsonify({
        "table": TABLE_CAP,
        "record": record,
        "data": data,
        "bmcsetup_choices": Model().get_node_source_choices('bmcsetup', data.get('bmcsetup'), bmc_src),
        "osimage_choices": Model().get_node_source_choices('osimage', data.get('osimage'), os_src),
        "group_list": Model().get_list_options_json('group', data.get('group')),
        "switch_list": Model().get_list_options_json('switch', data.get('switch')),
        "network_list": Model().get_list_options_json('network'),
        "bond_modes": Helper().get_bond_mode_list(),
    })


@app.route('/delete/<string:record>', methods=['GET'])
def delete(record=None):
    response = Rest().get_delete(TABLE, record)
    LOGGER.info(f'{response.status_code} {response.content}')
    if response.status_code == 204:
        return jsonify({"message": f'{TABLE_CAP}, {record} is deleted.', "status": "success"}), 204
    return jsonify({"message": "Something went wrong!", "status": "error"}), response.status_code


@app.route('/remove/<string:record>/<string:interface>', methods=['GET'])
def remove(record=None, interface=None):
    uri = record+'/interfaces/'+interface
    response = Rest().get_delete(TABLE, uri)
    LOGGER.info(f'{response.status_code} {response.content}')
    if response.status_code == 204:
        return jsonify({"message": f'{interface} Deleted from {TABLE_CAP} {record}.', "status": "success"}), 204
    return jsonify({"message": "Something went wrong!", "status": "error"}), response.status_code


@app.route('/clone/<string:record>', methods=['GET', 'POST'])
def clone(record=None):
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload["service"] = True if 'service' in payload else False
        payload = Helper().prepare_payload(None, payload)

        osimage = payload.get('osimage') or ''
        if '(group)' in osimage:
            payload['osimage'] = ''
        elif '(' in osimage and ')' in osimage:
            payload['osimage'] = osimage.split('(', 1)[0]

        bmcsetup = payload.get('bmcsetup') or ''
        if '(group)' in bmcsetup:
            payload['bmcsetup'] = ''
        elif '(' in bmcsetup and ')' in bmcsetup:
            payload['bmcsetup'] = bmcsetup.split('(', 1)[0]

        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, TABLE, payload)
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_clone(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 201:
            new_name = payload.get('newnodename') or payload.get('name')
            return jsonify({"message": f'{TABLE_CAP} cloned as {new_name}.', "status": "success"}), 201
        try:
            response_json = response.json()
            error = f'{response.status_code} - {response_json["message"]}'
        except json.decoder.JSONDecodeError:
            error = f'{response.status_code} - {response.content}'
        return jsonify({"message": error, "status": "error"}), response.status_code

    if not _wants_json():
        return home()
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if not table_data:
        return jsonify({"data": {}, "record": record, "error": f'{record} not found.'}), 404
    data = table_data['config'][TABLE][record]
    data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
    data = Helper().prepare_json(data)
    bmc_src, os_src = _node_os_bmc_sources(data)
    data = deepcopy(data)
    if 'interfaces' in data:
        for iface in data['interfaces']:
            if iface.get('macaddress') is not None:
                iface['macaddress'] = ''
            if 'ipaddress' in iface and iface.get('network'):
                nip = _next_free_ip(iface['network'])
                if nip:
                    iface['ipaddress'] = nip
    return jsonify({
        "table": TABLE_CAP,
        "record": record,
        "data": data,
        "bmcsetup_choices": Model().get_node_source_choices('bmcsetup', data.get('bmcsetup'), bmc_src),
        "osimage_choices": Model().get_node_source_choices('osimage', data.get('osimage'), os_src),
        "group_list": Model().get_list_options_json('group', data.get('group')),
        "switch_list": Model().get_list_options_json('switch', data.get('switch')),
        "network_list": Model().get_list_options_json('network'),
        "bond_modes": Helper().get_bond_mode_list(),
    })


@app.route('/osgrab/<string:record>', methods=['GET', 'POST'])
def osgrab(record=None):
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        uri = f'config/{TABLE}/{payload["name"]}/_osgrab'
        response = Rest().post_raw(uri, request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        response_json = response.json()
        if response.status_code == 200:
            result = {"message": response_json['message'], "status": "success"}
            if 'request_id' in response_json:
                result['request_id'] = response_json['request_id']
            return jsonify(result), 200
        return jsonify({"message": f'{response.status_code} - {response_json["message"]}', "status": "error"}), response.status_code

    if not _wants_json():
        return home()
    data = {}
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    node_list = Model().get_list_options_json('node', record)
    osimage_list = Model().get_list_options_json('osimage')
    if table_data:
        raw_data = table_data['config'][TABLE][record]
        data = Helper().prepare_json(raw_data)
        osimage_list = Model().get_list_options_json('osimage', data.get('osimage'))
    return jsonify({
        "table": TABLE_CAP,
        "record": record,
        "data": data,
        "node_list": node_list,
        "osimage_list": osimage_list,
    })


@app.route('/ospush/<string:record>', methods=['GET', 'POST'])
def ospush(record=None):
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        uri = f'config/{TABLE}/{payload["name"]}/_ospush'
        response = Rest().post_raw(uri, request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        response_json = response.json()
        if response.status_code == 200:
            result = {"message": response_json['message'], "status": "success"}
            if 'request_id' in response_json:
                result['request_id'] = response_json['request_id']
            return jsonify(result), 200
        return jsonify({"message": f'{response.status_code} - {response_json["message"]}', "status": "error"}), response.status_code

    if not _wants_json():
        return home()
    data = {}
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    node_list = Model().get_list_options_json('node', record)
    osimage_list = Model().get_list_options_json('osimage')
    if table_data:
        raw_data = table_data['config'][TABLE][record]
        data = Helper().prepare_json(raw_data)
        osimage_list = Model().get_list_options_json('osimage', data.get('osimage'))
    return jsonify({
        "table": TABLE_CAP,
        "record": record,
        "data": data,
        "node_list": node_list,
        "osimage_list": osimage_list,
    })


@app.route('/check_status/<string:status>/status/<string:request_id>', methods=['GET'])
def check_status(status=None, request_id=None):
    if request:
        uri = f'{status}/status/{request_id}'
        result = Rest().get_raw(uri)
        if not result:
            return jsonify({"message": "No response from daemon", "status_code": None}), 502
        try:
            body = result.json()
        except ValueError:
            text = (result.text or "").strip()
            return jsonify({
                "message": "Daemon returned non-JSON body",
                "status_code": result.status_code,
                "body": text,
            }), 200 if result.ok else result.status_code
        return jsonify(body), result.status_code
    return jsonify({"message": "No Response"})


@app.route('/license', methods=['GET'])
def license_info():
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
