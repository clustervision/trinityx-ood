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
Flask API + Vue SPA (app/index.html Jinja shell; Vue build in app/assets/, same as rack).
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
# SPA: Jinja shell in app/index.html; built Vue assets in app/assets (vite outDir), like rack.
app = Flask(__name__, static_folder="app/assets", template_folder="app")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

if APP_STATE is False:
    CORS(app, resources={r"/*": {"origins": "http://localhost:5174"}})


def _next_free_ip(network):
    if not network:
        return None
    uri = f'{network}/_nextfreeip'
    nextip = Rest().get_data('network', uri)
    if "status" in nextip and nextip["status"] is True:
        return nextip['content']['config']['network'][network].get('nextip')
    return None


def _node_record_for_response(table_data, record):
    """
    Daemon body (after status/content unwrap) -> node dict for *record*, or None.
    Same idea as group's _group_record_for_response (avoids KeyError).
    """
    if not table_data or not isinstance(table_data, dict):
        return None
    cmap = table_data.get('config', {}).get(TABLE)
    if not isinstance(cmap, dict) or record not in cmap:
        return None
    return cmap[record]


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
        if "status" not in table_data or table_data["status"] is not True:
            empty["error"] = f'No {TABLE_CAP} Available at this time.'
            return jsonify(empty)
        table_data = table_data['content']
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
    """
    Same as group: error page template, HTTP 200 (not 404).
    """
    return render_template("error.html", table=TABLE_CAP, data="", error=f"ERROR :: {e}"), 200


@app.route('/', methods=['GET'])
def home():
    """
    Serve the Vue SPA shell. window.APP_URL is this app's base URL.
    """
    url = {"APP_URL": f"{request.scheme}://{request.host}{request.path}"}
    return render_template("index.html", APP_URL=url["APP_URL"])


@app.route('/nodes', methods=['GET'])
def api_nodes():
    """
    JSON list of all nodes for the Vue frontend table.
    Always returns HTTP 200 with { fields, nodes, error } when the handler runs.
    """
    return _nodes_inventory_json()


@app.route('/api/v1/all_nodes', methods=['GET'])
def all_nodes():
    """
    Get a JSON list of all nodes for the Vue frontend table.
    """
    response = Rest().get_data(TABLE)
    return response


@app.route('/api/v1/get_resources', methods=['GET'])
@app.route('/api/v1/get_resources/<string:record>', methods=['GET'])
def get_resources(record: str = ""):
    """
    Get a JSON list of all get_resources for the Vue frontend table.
    """
    if record:
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        if "status" in table_data:
            if table_data["status"] is True:
                table_data = table_data['content']
            else:
                return jsonify(table_data)
        else:
            return jsonify(table_data)

        group_list = Model().get_list_options_json('group', record)
        bmcsetup_list = Model().get_list_options_json('bmcsetup', record)
        osimage_list = Model().get_list_options_json('osimage', record)
        switch_list = Model().get_list_options_json('switch', record)
        network_list = Model().get_list_options_json('network', record)
        bond_modes = Helper().get_bond_mode_list()
    else:
        group_list = Model().get_list_options_json('group')
        bmcsetup_list = Model().get_list_options_json('bmcsetup')
        osimage_list = Model().get_list_options_json('osimage')
        switch_list = Model().get_list_options_json('switch')
        network_list = Model().get_list_options_json('network')
        bond_modes = Helper().get_bond_mode_list()
    body = {
        "group_list": group_list,
        "bmcsetup_list": bmcsetup_list,
        "osimage_list": osimage_list,
        "switch_list": switch_list,
        "network_list": network_list,
        "bond_modes": bond_modes,
    }
    return jsonify(body)


@app.route('/show/<string:record>', methods=['GET'])
def show(record=None):
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if not table_data:
        return jsonify({"node": {}, "error": f'{record} From {TABLE_CAP} is Not available at this time'})
    if "status" in table_data:
        if table_data["status"] is True:
            table_data = table_data['content']
        else:
            return jsonify({"node": {}, "error": f'{record} From {TABLE_CAP} is Not available at this time'})
    raw_data = _node_record_for_response(table_data, record)
    if raw_data is None:
        return jsonify({"node": {}, "error": f'{record} From {TABLE_CAP} is Not available at this time'})
    raw_data = Helper().prepare_json(raw_data)
    node = Helper().filter_data_col_json(TABLE, raw_data)
    return jsonify({"node": node, "error": ""})


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


@app.route('/add', methods=['POST'])
def add():
    """
    This Method will add a requested record.
    """
    payload = {k: v for k, v in request.form.items() if v not in [None, '']}
    payload["service"] = True if 'service' in payload else False
    payload["setupbmc"] = True if 'setupbmc' in payload else False
    payload["netboot"] = True if 'netboot' in payload else False
    payload["bootmenu"] = True if 'bootmenu' in payload else False
    table_data = Rest().get_data(TABLE, payload['name'])
    if "status" in table_data:
        if table_data["status"] is True:
            if payload['name'] in table_data['content']['config'][TABLE]:
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
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if "status" in table_data:
        if table_data["status"] is True:
            table_data = table_data['content']
        else:
            return jsonify({"data": {}, "error": f'{record} not found.'}), 404
    else:
        return jsonify({"data": {}, "error": f'{record} not found.'}), 404
    raw_data = _node_record_for_response(table_data, record)
    if raw_data is None:
        return jsonify({"data": {}, "error": f'{record} not found.'}), 404
    data = {'name': raw_data['name'], 'newname': ''}
    return jsonify({"data": data, "error": ""})


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

    data = {}
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if "status" in table_data:
        if table_data["status"] is True:
            table_data = table_data['content']
        else:
            return jsonify({"data": {}, "record": record, "error": f'{record} not found.'}), 404
    else:
        return jsonify({"data": {}, "record": record, "error": f'{record} not found.'}), 404
    raw = _node_record_for_response(table_data, record)
    if raw is None:
        return jsonify({"data": {}, "record": record, "error": f'{record} not found.'}), 404
    data = {k: v for k, v in raw.items() if v not in [None, '', 'None']}
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


@app.route('/api/v1/delete/<string:record>', methods=['DELETE'])
def delete(record=None):
    """
    This Method will delete a requested record.
    """
    response = Rest().get_delete(TABLE, record)
    LOGGER.info(response)
    return response


@app.route('/remove/<string:record>/<string:interface>', methods=['GET'])
def remove(record=None, interface=None):
    """
    This Method will delete a requested interface from a record.
    """
    uri = record+'/interfaces/'+interface
    response = Rest().get_delete(TABLE, uri)
    LOGGER.info(response)
    return response


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

    data = {}
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if "status" in table_data:
        if table_data["status"] is True:
            table_data = table_data['content']
        else:
            return jsonify({"data": {}, "record": record, "error": f'{record} not found.'}), 404
    else:
        return jsonify({"data": {}, "record": record, "error": f'{record} not found.'}), 404
    raw = _node_record_for_response(table_data, record)
    if raw is None:
        return jsonify({"data": {}, "record": record, "error": f'{record} not found.'}), 404
    data = {k: v for k, v in raw.items() if v not in [None, '', 'None']}
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

    data = {}
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    node_list = Model().get_list_options_json('node', record)
    osimage_list = Model().get_list_options_json('osimage')
    if "status" in table_data:
        if table_data["status"] is True:
            table_data = table_data['content']
            raw_data = _node_record_for_response(table_data, record)
            if raw_data is not None:
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

    data = {}
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    node_list = Model().get_list_options_json('node', record)
    osimage_list = Model().get_list_options_json('osimage')
    if "status" in table_data:
        if table_data["status"] is True:
            table_data = table_data['content']
            raw_data = _node_record_for_response(table_data, record)
            if raw_data is not None:
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
