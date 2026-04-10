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

import os
import json
from flask import Flask, request, jsonify
from rest import Rest
from constant import LICENSE, TOKEN_FILE, APP_STATE
from helper import Helper
from log import Log
from model import Model

LOGGER = Log.init_log('INFO')
TABLE = 'group'
TABLE_CAP = 'Group'
app = Flask(__name__, static_folder="static")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

if APP_STATE is False: 
    app.config["DEBUG"] = True
    os.environ["FLASK_ENV"] = "development"


@app.before_request
def validate_home_directory():
    """
    Validate the $HOME directory of the user before proceeding further.
    """
    if request.path.startswith('/static/'):
        return
    if isinstance(TOKEN_FILE, dict):
        return jsonify({"error": TOKEN_FILE["error"]}), 500
    return None


@app.errorhandler(404)
def page_not_found(e):
    """
    Return JSON error on 404.
    """
    return jsonify({"error": f"ERROR :: {e}"}), 404


@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application. It will list all Groups which is available with daemon.
    """
    table_data = Rest().get_data(TABLE)
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config'][TABLE]
        raw_data = Helper().prepare_json(raw_data, True)
        fields, groups = Helper().filter_data_json(TABLE, raw_data)
        return jsonify({"fields": fields, "groups": groups, "error": ""})
    return jsonify({"fields": [], "groups": [], "error": f'No {TABLE_CAP} Available at this time.'})


@app.route('/show/<string:record>', methods=['GET'])
def show(record=None):
    """
    This Method will show a specific record.
    """
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config'][TABLE][record]
        raw_data = Helper().prepare_json(raw_data)
        group = Helper().filter_data_col_json(TABLE, raw_data)
        return jsonify({"group": group, "error": ""})
    return jsonify({"group": {}, "error": f'{record} From {TABLE_CAP} is Not available at this time'})


@app.route('/get_list/<string:table>', methods=['GET', 'POST'])
def get_list(table=None):
    """
    This method will return the list of element in table for as option for select tag.
    """
    if request:
        response = Model().get_list_options(table)
        return jsonify(response)
    return jsonify([])


@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    This Method will add a requested record.
    """
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        table_data = Rest().get_data(TABLE, payload['name'])
        if table_data:
            if payload['name'] in table_data['config'][TABLE]:
                return jsonify({"message": f'{payload["name"]} is already present in the database.', "status": "error"}), 409
        payload = Helper().prepare_payload(payload)

        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, TABLE, payload)
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_data(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 201:
            return jsonify({"message": f'{TABLE_CAP}, {payload["name"]} Created.', "status": "success"}), 201
        else:
            response_json = response.json()
            return jsonify({"message": f'{response.status_code} - {response_json["message"]}', "status": "error"}), response.status_code
    else:
        bmcsetup_list = Model().get_list_options_json('bmcsetup')
        osimage_list = Model().get_list_options_json('osimage')
        network_list = Model().get_list_options_json('network')
        return jsonify({
            "table": TABLE_CAP,
            "bmcsetup_list": bmcsetup_list,
            "osimage_list": osimage_list,
            "network_list": network_list,
            "bond_modes": Helper().get_bond_mode_list(),
        })


@app.route('/rename/<string:record>', methods=['GET', 'POST'])
def rename(record=None):
    """
    This method will Rename the Group.
    """
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload['name'] = payload['name']
        payload['newgroupname'] = payload['newname']
        del payload['newname']
        response = Helper().update_record(TABLE, payload)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            return jsonify({"message": f'{TABLE_CAP} renamed to {payload["newgroupname"]}.', "status": "success"}), 204
        else:
            response_json = response.json()
            return jsonify({"message": f'{response.status_code} - {response_json["message"]}', "status": "error"}), response.status_code
    elif request.method == 'GET':
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        if table_data:
            raw_data = table_data['config'][TABLE][record]
            data = {'name': raw_data['name'], 'newname': ''}
            return jsonify({"data": data, "error": ""})
        return jsonify({"data": {}, "error": f'{record} not found.'}), 404


@app.route('/edit/<string:record>', methods=['GET', 'POST'])
def edit(record=None):
    """
    This Method will edit a requested record.
    """
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None]}
        payload = Helper().prepare_payload(payload)
        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, TABLE, payload)

        if payload.get('bmcsetupname') == '':
            del payload['bmcsetupname']
        if payload.get('osimage') == '':
            del payload['osimage']
        if payload.get('osimagetag') == '':
            del payload['osimagetag']
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_data(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            return jsonify({"message": f'{TABLE_CAP}, {payload["name"]} Updated.', "status": "success"}), 204
        elif response.status_code == 201:
            response_json = response.json()
            return jsonify({"message": f'{TABLE_CAP} {response_json["message"]}.', "status": "success"}), 201
        else:
            response_json = response.json()
            return jsonify({"message": f'{response.status_code} - {response_json["message"]}', "status": "error"}), response.status_code
    else:
        data = {}
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        if table_data:
            data = table_data['config'][TABLE][record]
            data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
            data = Helper().prepare_json(data)

        bmcsetup_list = Model().get_list_options_json('bmcsetup', data.get('bmcsetupname'))
        osimage_list = Model().get_list_options_json('osimage', data.get('osimage'))
        network_list = Model().get_list_options_json('network')

        return jsonify({
            "table": TABLE_CAP,
            "record": record,
            "data": data,
            "bmcsetup_list": bmcsetup_list,
            "osimage_list": osimage_list,
            "network_list": network_list,
            "bond_modes": Helper().get_bond_mode_list(),
        })


@app.route('/delete/<string:record>', methods=['GET'])
def delete(record=None):
    """
    This Method will delete a requested record.
    """
    response = Rest().get_delete(TABLE, record)
    LOGGER.info(f'{response.status_code} {response.content}')
    if response.status_code == 204:
        return jsonify({"message": f'{TABLE_CAP}, {record} is deleted.', "status": "success"}), 204
    return jsonify({"message": "Something went wrong!", "status": "error"}), response.status_code


@app.route('/remove/<string:record>/<string:interface>', methods=['GET'])
def remove(record=None, interface=None):
    """
    This Method will remove an interface from a record.
    """
    uri = record+'/interfaces/'+interface
    response = Rest().get_delete(TABLE, uri)
    LOGGER.info(f'{response.status_code} {response.content}')
    if response.status_code == 204:
        return jsonify({"message": f'{interface} Deleted from {TABLE_CAP} {record}.', "status": "success"}), 204
    return jsonify({"message": "Something went wrong!", "status": "error"}), response.status_code


@app.route('/clone/<string:record>', methods=['GET', 'POST'])
def clone(record=None):
    """
    This Method will clone a requested record.
    """
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None]}
        payload = Helper().prepare_payload(payload)

        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, TABLE, payload)

        if payload.get('bmcsetupname') == '':
            del payload['bmcsetupname']
        if payload.get('osimage') == '':
            del payload['osimage']
        if payload.get('osimagetag') == '':
            del payload['osimagetag']
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_clone(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 201:
            return jsonify({"message": f'{TABLE_CAP} cloned as {payload["name"]}.', "status": "success"}), 201
        else:
            try:
                response_json = response.json()
                error = f'{response.status_code} - {response_json["message"]}'
            except json.decoder.JSONDecodeError:
                error = f'{response.status_code} - {response.content}'
            return jsonify({"message": error, "status": "error"}), response.status_code
    else:
        data = {}
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        if table_data:
            data = table_data['config'][TABLE][record]
            data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
            data = Helper().prepare_json(data)

        bmcsetup_list = Model().get_list_options_json('bmcsetup', data.get('bmcsetupname'))
        osimage_list = Model().get_list_options_json('osimage', data.get('osimage'))
        network_list = Model().get_list_options_json('network')

        return jsonify({
            "table": TABLE_CAP,
            "record": record,
            "data": data,
            "bmcsetup_list": bmcsetup_list,
            "osimage_list": osimage_list,
            "network_list": network_list,
            "bond_modes": Helper().get_bond_mode_list(),
        })


@app.route('/member/<string:table>/<string:record>', methods=['GET'])
def member(table=None, record=None):
    """
    This Method will provide all the member nodes for the requested record.
    """
    get_member = Rest().get_data(table, record+'/_member')
    LOGGER.info(get_member)
    if get_member:
        data = get_member['config'][table][record]['members']
        data = Helper().prepare_json(data)
        return jsonify({"members": data, "error": ""})
    return jsonify({"members": [], "error": f'{record} From {table.capitalize()} does not have any members at this time.'})


@app.route('/ospush/<string:record>', methods=['GET', 'POST'])
def ospush(record=None):
    """
    This method handles OS Push for a group.
    """
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        request_data = {'config':{TABLE:{payload['name']: payload}}}
        uri = f'config/{TABLE}/{payload["name"]}/_ospush'
        response = Rest().post_raw(uri, request_data)
        response_json = response.json()

        if response.status_code == 200:
            result = {"message": response_json['message'], "status": "success"}
            if 'request_id' in response_json:
                result['request_id'] = response_json['request_id']
            return jsonify(result), 200
        else:
            return jsonify({"message": f'{response.status_code} - {response_json["message"]}', "status": "error"}), response.status_code

    elif request.method == 'GET':
        data = {}
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        group_list = Model().get_list_options_json('group', record)
        osimage_list = Model().get_list_options_json('osimage')
        if table_data:
            raw_data = table_data['config'][TABLE][record]
            data = Helper().prepare_json(raw_data)
            osimage_list = Model().get_list_options_json('osimage', data.get('osimage'))
        return jsonify({
            "table": TABLE_CAP,
            "record": record,
            "data": data,
            "group_list": group_list,
            "osimage_list": osimage_list,
        })


@app.route('/check_status/<string:status>/status/<string:request_id>', methods=['GET'])
def check_status(status=None, request_id=None):
    """
    This method will check the status of request on behalf of request ID.
    """
    if request:
        uri = f'{status}/status/{request_id}'
        result = Rest().get_raw(uri)
        return jsonify(result.json())
    return jsonify({"message": "No Response"})


@app.route('/license', methods=['GET'])
def license_info():
    """
    This Method will provide license in details.
    """
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
