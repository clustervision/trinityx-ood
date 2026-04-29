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

import types
import os
import json
from html import unescape
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
import urllib3
from flask_cors import CORS
from rest import Rest
from constant import INI_FILE, LICENSE, TOKEN_FILE, APP_STATE
from helper import Helper
from presenter import Presenter
from log import Log
from model import Model

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGER = Log.init_log('INFO')
TABLE = 'group'
TABLE_CAP = 'Group'
# SPA: Jinja shell in app/index.html; built Vue assets in app/assets (vite outDir).
app = Flask(__name__, static_folder="app/assets", template_folder="app")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

if APP_STATE is False:
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})




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


def _group_record_for_response(table_data, record):
    """
    Return the group dict for *record* from a daemon get_data payload, or None
    (avoids KeyError when the id is missing, e.g. after a bad merge / rollback).
    """
    if not table_data or not isinstance(table_data, dict):
        return None
    gmap = table_data.get('config', {}).get(TABLE)
    if not isinstance(gmap, dict) or record not in gmap:
        return None
    return gmap[record]



@app.errorhandler(404)
def page_not_found(e):
    """
    This method will redirect to error Template Page with Error Message on 404.
    """
    return render_template("error.html", table=TABLE_CAP, data="", error=f"ERROR :: {e}"), 200


@app.route('/', methods=['GET'])
def home():
    """
    Serve the Vue SPA shell. window.APP_URL is this app's base URL.
    """
    url = Helper().app_url(request)
    return render_template(
        "index.html",
        APP_URL=url["APP_URL"],
    )


@app.route('/api/groups', methods=['GET'])
def api_groups():
    """
    JSON list of all groups for the Vue frontend table.
    Always returns HTTP 200 with { fields, groups, error } when the handler runs.
    """
    empty = {"fields": [], "groups": [], "error": ""}
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
            empty["error"] = 'Group data from daemon is not a mapping; check Luna daemon response.'
            return jsonify(empty)
        raw_data = Helper().prepare_json(raw_data, True)
        fields, groups = Helper().filter_data_json(TABLE, raw_data)
        return jsonify({"fields": fields, "groups": groups, "error": ""})
    except Exception as exc:
        LOGGER.exception("api_groups failed")
        return jsonify({
            "fields": [],
            "groups": [],
            "error": f'api_groups: {exc}',
        })


@app.route('/show/<string:record>', methods=['GET'])
def show(record=None):
    """
    This Method will show a specific record.
    """
    data, error = "", ""
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config'][TABLE][record]
        raw_data = Helper().prepare_json(raw_data)
        fields, rows  = Helper().filter_data_col(TABLE, raw_data)
        data = Presenter().show_table_col(fields, rows)
        data = unescape(data)
    else:
        error = f'{record} From {TABLE_CAP} is Not available at this time'
    return render_template("info.html", table=TABLE_CAP, data=data, error=error, record=record)


@app.route('/get_list/<string:table>', methods=['GET', 'POST'])
def get_list(table=None):
    """
    This method will return the list of element in table for as option for select tag.
    """
    response = None
    if request:
        response = Model().get_list_options(table)
        response = json.dumps(response)
    return response


@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    This Method will add a requested record.
    """
    page = types.SimpleNamespace()
    page.name = f"Add New {TABLE_CAP}"
    bmcsetup_list = Model().get_list_option_html('bmcsetup')
    osimage_list = Model().get_list_option_html('osimage')
    network_list = Model().get_list_option_html('network')
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        table_data = Rest().get_data(TABLE, payload['name'])
        if table_data:
            if payload['name'] in table_data['config'][TABLE]:
                error = f'HTTP ERROR :: {payload["name"]} is already present in the database.'
                flash(error, "error")
                return redirect(url_for('add'), code=302)
        payload = Helper().prepare_payload(payload)

        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, TABLE, payload)
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_data(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 201:
            flash(f'{TABLE_CAP}, {payload["name"]} Created.', "success")
            return redirect(url_for('home'), code=302)
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
            return redirect(url_for('add'), code=302)
    else:
        bmcsetup_list = Model().get_list_options_json('bmcsetup')
        osimage_list = Model().get_list_options_json('osimage')
        network_list = Model().get_list_options_json('network')
        bond_modes = Helper().get_bond_mode_list()
        body = {
            "table": TABLE_CAP,
            "bmcsetup_list": bmcsetup_list,
            "osimage_list": osimage_list,
            "network_list": network_list,
            "bond_modes": bond_modes,
        }
        return jsonify(body)


@app.route('/rename/<string:record>', methods=['GET', 'POST'])
def rename(record=None):
    """
    This method will Rename the BMC Setup.
    """
    data = {}
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload['name'] = payload['name']
        payload['newgroupname'] = payload['newname']
        del payload['newname']
        response = Helper().update_record(TABLE, payload)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            flash(f'{TABLE_CAP} renamed to {payload["name"]}.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('rename', record=payload['newgroupname']), code=302)
    elif request.method == 'GET':
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        if table_data:
            raw_data = table_data['config'][TABLE][record]
            data = {'name': raw_data['name'], 'newname': ''}
    return render_template("rename.html", table=TABLE_CAP, data=data)


@app.route('/edit/<string:record>', methods=['GET', 'POST'])
def edit(record=None):
    """
    Edit an existing group (JSON for Vue; TRIX-1742 style).
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
        if response.status_code == 201:
            response_json = response.json()
            return jsonify({"message": f'{TABLE_CAP} {response_json["message"]}.', "status": "success"}), 201
        response_json = response.json()
        return jsonify(
            {"message": f'{response.status_code} - {response_json["message"]}', "status": "error"},
        ), response.status_code

    data = {}
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    raw = _group_record_for_response(table_data, record)
    if raw is not None:
        data = {k: v for k, v in raw.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)

    bmcsetup_list = Model().get_list_options_json('bmcsetup', data.get('bmcsetupname'))
    osimage_list = Model().get_list_options_json('osimage', data.get('osimage'))
    network_list = Model().get_list_options_json('network')
    bond_modes = Helper().get_bond_mode_list()
    return jsonify({
        "table": TABLE_CAP,
        "record": record,
        "data": data,
        "bmcsetup_list": bmcsetup_list,
        "osimage_list": osimage_list,
        "network_list": network_list,
        "bond_modes": bond_modes,
    })


@app.route('/delete/<string:record>', methods=['GET'])
def delete(record=None):
    """
    This Method will delete a requested record.
    """
    response = Rest().get_delete(TABLE, record)
    LOGGER.info(f'{response.status_code} {response.content}')
    if response.status_code == 204:
        flash(f'{TABLE_CAP}, {record} is deleted.', "success")
    else:
        flash('ERROR :: Something went wrong!', "error")
    return redirect(url_for('home'), code=302)


@app.route('/remove/<string:record>/<string:interface>', methods=['GET'])
def remove(record=None, interface=None):
    """
    This Method will delete a requested record.
    """
    result = {}
    uri = record+'/interfaces/'+interface
    response = Rest().get_delete(TABLE, uri)
    LOGGER.info(f'{response.status_code} {response.content}')
    if response.status_code == 204:
        result['success'] = f'{interface} Deleted from {TABLE_CAP} {record}.'
    else:
        result['error'] = 'ERROR :: Something went wrong!'
    result = json.dumps(result)
    return result


@app.route('/clone/<string:record>', methods=['GET', 'POST'])
def clone(record=None):
    """
    Clone a group (JSON for Vue; TRIX-1742 style).
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
            return jsonify({"message": f'{TABLE_CAP} cloned as {payload.get("name")}.', "status": "success"}), 201
        try:
            response_json = response.json()
            error = f'{response.status_code} - {response_json["message"]}'
        except json.decoder.JSONDecodeError:
            error = f'{response.status_code} - {response.content}'
        return jsonify({"message": error, "status": "error"}), response.status_code

    data = {}
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    raw = _group_record_for_response(table_data, record)
    if raw is not None:
        data = {k: v for k, v in raw.items() if v not in [None, '', 'None']}
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
        num = 1
        fields = ['S.No.', 'Nodes']
        rows = []
        for node in data:
            new_row = [num, node]
            rows.append(new_row)
            num = num + 1
        response = Presenter().show_table(fields, rows, True)
    else:
        response = f'{record} From {table.capitalize()} Not have any members at this time.'
    response = json.dumps(response)
    return response


@app.route('/ospush/<string:record>', methods=['GET', 'POST'])
def ospush(record=None):
    """
    This method will open the Login Page(First Page)
    """
    data = {}
    osimage_list = ''
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        request_data = {'config':{TABLE:{payload['name']: payload}}}
        uri = f'config/{TABLE}/{payload["name"]}/_ospush'
        response = Rest().post_raw(uri, request_data)
        response_json = response.json()

        if response.status_code == 200:
            flash(response_json['message'], "success")
            if 'request_id' in response_json:
                return redirect(url_for('ospush', record = record, request_id=response_json['request_id'], message=response_json['message']), code=302)
        else:
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('ospush', record=record), code=302)
    

    elif request.method == 'GET':
        table_data = Rest().get_data(TABLE, record)
        LOGGER.info(table_data)
        group_list = Model().get_list_option_html('group', record)
        if table_data:
            raw_data = table_data['config'][TABLE][record]
            data = Helper().prepare_json(raw_data)
            osimage_list = Model().get_list_options_json('osimage', data.get('osimage'))
        body = {
            "table": TABLE_CAP,
            "record": record,
            "data": data,
            "group_list": group_list,
            "osimage_list": osimage_list,
        }
        return jsonify(body)


@app.route('/check_status/<string:status>/status/<string:request_id>', methods=['GET'])
def check_status(status=None, request_id=None):
    """
    This method will check the status of request on behalf of request ID.
    """
    response = {"message": "No Response"}
    if request:
        uri = f'{status}/status/{request_id}'
        result = Rest().get_raw(uri)
        response = result.json()
    response = json.dumps(response)
    return response


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
        _ssl_crt = '/trinity/local/etc/ssl/yixin3-dev-ctrl001.cluster.crt'
        _ssl_key = '/trinity/local/etc/ssl/yixin3-dev-ctrl001.cluster.key'
        if os.path.isfile(_ssl_crt) and os.path.isfile(_ssl_key):
            dev_context = (_ssl_crt, _ssl_key)
            app.run(host='0.0.0.0', port=7755, debug=True, ssl_context=dev_context)
        else:
            app.run(host='0.0.0.0', port=7755, debug=True)
    else:
        app.run()

# Run in Dev mode with TLS (read certs as the app user):
# sudo setfacl -m u:admin:r /trinity/local/etc/ssl/yixin3-dev-ctrl001.cluster.*
# sudo -u admin bash -c '. /trinity/local/python/bin/activate && python app.py'
