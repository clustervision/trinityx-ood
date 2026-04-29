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
from flask import Flask, request, jsonify, render_template
from rest import Rest
from constant import LICENSE, INI_FILE, TOKEN_FILE, APP_STATE
from helper import Helper
from log import Log
from model import Model


LOGGER = Log.init_log('INFO')
TABLE = 'osimage'
TABLE_CAP = 'OS Image'
app = Flask(__name__, static_folder="static")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


if APP_STATE is False: 
    app.config["DEBUG"] = True
    os.environ["FLASK_ENV"] = "development"


def _chroot_base_url(req):
    """Same shell URL pattern as legacy inventory.html."""
    if req.headers and "X-Forwarded-Proto" in dict(req.headers):
        scheme = dict(req.headers)["X-Forwarded-Proto"]
    else:
        scheme = req.scheme
    host_part = req.host.split(':')[0]
    return f"{scheme}://{req.host}/pun/sys/shell/ssh/{host_part}"


def _osimage_inventory_json():
    empty = {"fields": [], "images": [], "error": "", "chroot_base_url": ""}
    try:
        chroot_url = _chroot_base_url(request)
        LOGGER.info(f"chroot_Base_url: {chroot_url}")
        empty["chroot_base_url"] = chroot_url
        table_data = Rest().get_data(TABLE)
        LOGGER.info(table_data)
        if not table_data:
            empty["error"] = f'No {TABLE_CAP} Available at this time.'
            return jsonify(empty)
        raw_data = table_data['config'][TABLE]
        raw_data = Helper().prepare_json(raw_data, True)
        fields, images = Helper().filter_data_json(TABLE, raw_data)
        for img in images:
            path = img.get('path')
            kv = img.get('kernelversion')
            name = img.get('name')
            if path and kv and ">None<" not in str(kv):
                img["chroot_session_url"] = (
                    f"{chroot_url}/image={name},path={path},kernel_version={kv}"
                )
            else:
                img["chroot_session_url"] = None
        return jsonify({"fields": fields, "images": images, "error": "", "chroot_base_url": chroot_url})
    except Exception as exc:
        LOGGER.exception("osimage inventory JSON failed")
        return jsonify({
            "fields": [],
            "images": [],
            "error": f"osimage inventory: {exc}",
            "chroot_base_url": "",
        })


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


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": f"ERROR :: {e}"}), 404


@app.route('/', methods=['GET'])
def home():
    """Inventory list as JSON."""
    return _osimage_inventory_json()


@app.route('/show/<string:record>', methods=['GET'])
def show(record=None):
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config'][TABLE][record]
        raw_data = Helper().prepare_json(raw_data)
        osimage_obj = Helper().filter_data_col_json(TABLE, raw_data)
        return jsonify({"table": TABLE_CAP, "record": record, "osimage": osimage_obj, "error": ""})
    return jsonify({"osimage": {}, "record": record, "error": f'{record} From {TABLE_CAP} is Not available at this time'}), 404


@app.route('/add', methods=['GET', 'POST'])
def add():
    page_name = f"Add New {TABLE_CAP}"
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        table_data = Rest().get_data(TABLE, payload['name'])
        if table_data:
            if payload['name'] in table_data['config'][TABLE]:
                return jsonify({"message": f'{payload["name"]} is already present in the database.', "status": "error"}), 409
        payload = Helper().prepare_payload(None, payload)
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_data(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 201:
            return jsonify({"message": f'{TABLE_CAP}, {payload["name"]} Created.', "status": "success"}), 201
        response_json = response.json()
        return jsonify({"message": f'{response.status_code} - {response_json["message"]}', "status": "error"}), response.status_code
    return jsonify({"table": TABLE_CAP, "page_name": page_name})


@app.route('/rename/<string:record>', methods=['GET', 'POST'])
def rename(record=None):
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload['name'] = payload['name']
        payload['newosimage'] = payload['newname']
        del payload['newname']
        response = Helper().update_record(TABLE, payload)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            return jsonify({"message": f'{TABLE_CAP} renamed to {payload["newosimage"]}.', "status": "success"}), 204
        response_json = response.json()
        return jsonify({"message": f'{response.status_code} - {response_json["message"]}', "status": "error"}), response.status_code
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config'][TABLE][record]
        data = {'name': raw_data['name'], 'newname': ''}
        return jsonify({"data": data, "record": record, "error": ""})
    return jsonify({"data": {}, "record": record, "error": "Not found"}), 404


@app.route('/edit/<string:record>', methods=['GET', 'POST'])
def edit(record=None):
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    data = {}
    if table_data:
        data = table_data['config'][TABLE][record]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None]}
        payload = Helper().prepare_payload(TABLE, payload)
        if data.get('tag') == payload.get('tag'):
            del payload['tag']
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_data(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            return jsonify({"message": f'{TABLE_CAP}, {payload["name"]} Updated.', "status": "success"}), 204
        response_json = response.json()
        return jsonify({"message": f'{response.status_code} - {response_json["message"]}', "status": "error"}), response.status_code
    if not table_data:
        return jsonify({"data": {}, "record": record, "error": f'{record} not found.'}), 404
    return jsonify({"table": TABLE_CAP, "record": record, "data": data, "error": ""})


@app.route('/delete/<string:record>', methods=['GET'])
def delete(record=None):
    response = Rest().get_delete(TABLE, record)
    LOGGER.info(f'{response.status_code} {response.content}')
    if response.status_code == 204:
        return jsonify({"message": f'{TABLE_CAP}, {record} is deleted.', "status": "success"}), 204
    return jsonify({"message": "Something went wrong!", "status": "error"}), response.status_code


@app.route('/clone/<string:record>', methods=['GET', 'POST'])
def clone(record=None):
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    data = {}
    if table_data:
        data = table_data['config'][TABLE][record]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None]}
        for k, v in payload.items():
            if v == 'on':
                payload[k] = True
        prior = data
        if prior.get('tag') == payload.get('tag'):
            del payload['tag']
        response = Helper().clone_record(TABLE, payload)
        LOGGER.info(f'{response.status_code} {response.content}')
        response_json = response.json() if response.content else {}
        if response.status_code == 200:
            out = {"message": f'{TABLE_CAP}, {data["name"]} Cloned as {payload["newosimage"]}.', "status": "success"}
            if 'request_id' in response_json:
                out['request_id'] = response_json['request_id']
            if 'message' in response_json:
                out['daemon_message'] = response_json['message']
            return jsonify(out), 200
        return jsonify({"message": f'HTTP ERROR :: {response.status_code} - {response_json.get("message", "")}', "status": "error"}), response.status_code
    if not table_data:
        return jsonify({"data": {}, "record": record, "error": f'{record} not found.'}), 404
    return jsonify({"table": TABLE_CAP, "record": record, "data": data, "error": ""})


@app.route('/member/<string:table>/<string:record>', methods=['GET'])
def member(table=None, record=None):
    get_member = Rest().get_data(table, record+'/_member')
    LOGGER.info(get_member)
    if get_member:
        mdata = get_member['config'][table][record]['members']
        mdata = Helper().prepare_json(mdata)
        return jsonify({"table": table, "record": record, "members": mdata})
    return jsonify({"table": table, "record": record, "members": [], "error": f'{record} From {table.capitalize()} has no members at this time.'})


@app.route('/get_request/<string:status>/<string:service_name>/<string:action>', methods=['GET'])
def get_request(status=None, service_name=None, action=None):
    uri = f'{status}/{service_name}/{action}'
    if action == '_pack':
        uri = f'config/{uri}'
    result = Rest().get_raw(uri)
    if not result:
        return jsonify({"message": "No response from daemon"}), 502
    LOGGER.info(f'{result.status_code} {result.content}')
    try:
        body = result.json()
    except ValueError:
        return jsonify({"message": "Daemon returned non-JSON body", "status_code": result.status_code, "body": (result.text or "").strip()}), 200 if result.ok else result.status_code
    return jsonify(body)


@app.route('/check_status/<string:status>/status/<string:request_id>', methods=['GET'])
def check_status(status=None, request_id=None):
    uri = f'{status}/status/{request_id}'
    result = Rest().get_raw(uri)
    if not result:
        return jsonify({"message": "No response from daemon"}), 502
    LOGGER.info(f'{result.status_code} {result.content}')
    try:
        body = result.json()
    except ValueError:
        return jsonify({"message": "Daemon returned non-JSON body", "status_code": result.status_code, "body": (result.text or "").strip()}), 200 if result.ok else result.status_code
    return jsonify(body), result.status_code


@app.route('/kernel/<string:record>', methods=['GET', 'POST'])
def kernel(record=None):
    osimage_list = Model().get_list_options_json(TABLE, record)
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None]}
        for k, v in payload.items():
            if v == 'on':
                payload[k] = True
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_data(TABLE, payload['name']+'/kernel', request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            return jsonify({"message": f'{TABLE_CAP}, {record} Kernel updated.', "status": "success"}), 204
        if response.status_code == 200:
            response_json = response.json()
            out = {"message": f'{TABLE_CAP}, {record} Kernel updated.', "status": "success"}
            if 'request_id' in response_json:
                out['request_id'] = response_json['request_id']
            if 'message' in response_json:
                out['daemon_message'] = response_json['message']
            return jsonify(out), 200
        try:
            response_json = response.json()
            err_msg = response_json.get("message", "")
        except ValueError:
            err_msg = (response.text or "").strip()
        return jsonify({"message": f'{response.status_code} - {err_msg}', "status": "error"}), response.status_code

    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    data = {}
    if table_data and record is not None:
        raw_data = table_data['config'][TABLE][record]
        raw_data = {k: v for k, v in raw_data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(raw_data)
    if not table_data:
        return jsonify({"data": {}, "record": record, "osimage_list": osimage_list, "error": "Not found"}), 404
    return jsonify({"table": TABLE_CAP, "record": record, "data": data, "osimage_list": osimage_list, "error": ""})


@app.route('/get_record/<string:record>', methods=['GET', 'POST'])
def get_record(record=None):
    body = Model().get_record(TABLE, record)
    return jsonify(body)


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
