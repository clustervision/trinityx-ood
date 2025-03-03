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
This File is a Main File Luna 2 Switch.
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
from html import unescape
from flask import Flask, request, render_template, flash, url_for, redirect
from rest import Rest
from constant import LICENSE, TOKEN_FILE, APP_STATE
from helper import Helper
from presenter import Presenter
from log import Log
from model import Model

LOGGER = Log.init_log('INFO')
TABLE = 'switch'
TABLE_CAP = 'Switch'
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
        return render_template("error.html", table=TABLE_CAP, data="", error=TOKEN_FILE["error"])
    return None


@app.errorhandler(404)
def page_not_found(e):
    """
    This method will redirect to error Template Page with Error Message on 404.
    """
    return render_template("error.html", table=TABLE_CAP, data="", error=f"ERROR :: {e}"), 200


@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application. It will list all Switch which is available with daemon.
    """
    data, error = "", ""
    table_data = Rest().get_data(TABLE)
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config'][TABLE]
        raw_data = Helper().prepare_json(raw_data, True)
        fields, rows  = Helper().filter_data(TABLE, raw_data)
        data = Presenter().show_table(fields, rows)
        data = unescape(data)
    else:
        error = f'No {TABLE_CAP} Available at this time.'
    return render_template("inventory.html", table=TABLE_CAP, data=data, error=error)


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


@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    This Method will add a requested record.
    """
    page = types.SimpleNamespace()
    page.name = f"Add New {TABLE_CAP}"
    network_list = Model().get_list_options('network')
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        table_data = Rest().get_data(TABLE, payload['name'])
        if table_data:
            if payload['name'] in table_data['config'][TABLE]:
                error = f'HTTP ERROR :: {payload["name"]} is already present in the database.'
                flash(error, "error")
                return redirect(url_for('add'), code=302)
        payload = Helper().prepare_payload(None, payload)
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
        return render_template("add.html", table=TABLE_CAP, network_list=network_list, page=page)


@app.route('/rename/<string:record>', methods=['GET', 'POST'])
def rename(record=None):
    """
    This method will Rename the Switch.
    """
    data = {}
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload['name'] = payload['name']
        payload['newswitchname'] = payload['newname']
        del payload['newname']
        response = Helper().update_record(TABLE, payload)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            flash(f'{TABLE_CAP} renamed to {payload["name"]}.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('rename', record=payload['newswitchname']), code=302)
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
    This Method will update a requested record.
    """
    data = {}
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        data = table_data['config'][TABLE][record]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
        if 'network' in data:
            network_list = Model().get_list_options('network', data['network'])
        else:
            network_list = Model().get_list_options('network')
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None]}
        payload = Helper().prepare_payload(None, payload)
        request_data = {'config': {TABLE: {payload['name']: payload}}}
        response = Rest().post_data(TABLE, payload['name'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            flash(f'{TABLE_CAP}, {payload["name"]} Updated.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('edit', record=record), code=302)
    else:
        return render_template("edit.html", table=TABLE_CAP, record=record,  data=data, network_list=network_list)


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


@app.route('/clone/<string:record>', methods=['GET', 'POST'])
def clone(record=None):
    """
    This Method will clone a requested record.
    """
    data = {}
    table_data = Rest().get_data(TABLE, record)
    LOGGER.info(table_data)
    if table_data:
        data = table_data['config'][TABLE][record]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
        if 'network' in data:
            network_list = Model().get_list_options('network', data['network'])
        else:
            network_list = Model().get_list_options('network')
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None]}
        response = Helper().clone_record(TABLE, payload)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 201:
            flash(f'{TABLE_CAP}, {data["name"]} Cloned as {payload["name"]}.', "success")
            return redirect(url_for('home'), code=302)
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
            return redirect(url_for('clone', record=record), code=302)
    else:
        return render_template("clone.html", table=TABLE_CAP, record=record,  data=data, network_list=network_list)


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
        app.run(host='0.0.0.0', port=7755, debug=True)
    else:
        app.run()
