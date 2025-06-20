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
This File is a Main File Luna 2 Secrets.
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
from html import unescape
from flask import Flask, request, abort, render_template, flash, url_for, redirect
from log import Log
from rest import Rest
from constant import LICENSE, TOKEN_FILE, APP_STATE
from helper import Helper
from presenter import Presenter
from model import Model

logger = Log.init_log('INFO')
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
        return render_template("error.html", table="Secrets", data="", error=TOKEN_FILE["error"])
    return None


@app.errorhandler(404)
def page_not_found(e):
    """
    This method will redirect to error Template Page with Error Message on 404.
    """
    return render_template("error.html", table="Secrets", data="", error=f"ERROR :: {e}"), 200


@app.route('/', methods=['GET'])
@app.route('/<string:entity>', methods=['GET'])
def home(entity=None):
    """
    This is the main method of application. It will list all Secrets which is available with daemon.
    """
    table = 'secrets'
    secrets = True
    group_secrets, node_secrets = '', ''
    record=None
    secret=None
    uri = 'secrets'
    if record:
        uri = f'{uri}/{entity}/{record}'
        if secret:
            uri = f'{uri}/{secret}'
    secret_list = Rest().get_data(uri)
    if secret_list:
        secret_data = secret_list['config']['secrets']
        if 'group' in secret_data:
            fields, rows  =  Helper().get_secrets('groupsecrets', secret_data['group'])
            group_secrets = Presenter().show_table(fields, rows)
            group_secrets = unescape(group_secrets)
        if 'node' in secret_data:
            fields, rows  =  Helper().get_secrets('nodesecrets', secret_data['node'])
            node_secrets = Presenter().show_table(fields, rows)
            node_secrets = unescape(node_secrets)
    else:
        flash('Secrets are not available.', 'error')
        secrets = False
    if entity:
        if entity == 'group':
            node_secrets = ''
        elif entity == 'node':
            group_secrets = ''
        else:
            abort(404, None)

    return render_template("inventory.html", table = table.capitalize(), secrets=secrets, group_secrets=group_secrets, node_secrets=node_secrets, data=None, entity=entity)


@app.route('/show/<string:table>/<string:record>/<string:secret>', methods=['GET'])
def show(table=None, record=None, secret=None):
    """
    This Method will show a specific record.
    """
    data = ""
    entity = table.replace('secrets', '')
    table = 'secrets'
    entity_name = record
    secret_name = secret
    record = f'{entity}/{entity_name}/{secret_name}'
    table_data = Rest().get_data(table, record)
    if table_data:
        raw_data = table_data['config'][table][entity][entity_name]
        raw_data = Helper().prepare_json(raw_data)
        fields, rows  = Helper().filter_secret_col(
                entity+table,
                table_data['config'][table][entity]
            )
        data = Presenter().show_table_col(fields, rows)
        data = unescape(data)
    else:
        error = f'{record} From {table.capitalize()} is Not available at this time'
    return render_template("info.html", table = table.capitalize(), data = data, entity=entity, entity_name=entity_name, secret_name=secret_name, record=record)


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


@app.route('/add/<string:table>', methods=['GET', 'POST'])
def add(table=None):
    """
    This Method will add a requested record.
    """
    page = "Add New Secret"
    table_split = table.split('_')
    entity = table_split[0]
    table_name = table_split[1]
    table_capital = f'{entity.capitalize()} {table_name.capitalize()}'
    select_list = Model().get_list_option_html(entity)
    if request.method == 'POST':
        payload = Helper().prepare_payload(None, request.form)
        table_data = Rest().get_data('secrets', f'{entity}/{payload["name"]}/{payload["secret"]}')        
        if table_data:
            for each in table_data['config']['secrets'][entity][payload["name"]]:
                if payload['secret'] in each['name']:
                    error = f'HTTP ERROR :: {payload["secret"]} is already present in the {payload["name"]}.'
                    flash(error, "error")
                    return redirect(url_for('add', table=table), code=302)
        entity_name = payload['name']
        del payload['name']
        payload['name'] = payload['secret']
        del payload['secret']
        request_data = {'config': {'secrets': {entity: {entity_name: [payload]}}}}
        uri = f'{entity}/{entity_name}'
        response = Rest().post_data('secrets', uri, request_data)

        if response.status_code == 201:
            flash(f'{table_name.capitalize()}, {payload["name"]} Created.', "success")
            return redirect(url_for('home'), code=302)
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
            return redirect(url_for('add', table=table), code=302)
    else:
        return render_template("add.html", table = table_name.capitalize(), entity=entity, select_list=select_list, page=page)


@app.route('/edit/<string:table>/<string:record>/<string:secret>', methods=['GET', 'POST'])
def edit(table=None, record=None, secret=None):
    """
    This Method will add a requested record.
    """
    data = {}
    return_table = table
    entity = table.replace('secrets', '')
    table = 'secrets'
    entity_name = record
    secret_name = secret
    uri = f'{entity}/{entity_name}/{secret_name}'
    table_data = Rest().get_data(table, uri)
    if isinstance(table_data, dict):
        data = table_data['config'][table][entity][entity_name][0]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
    if request.method == 'POST':
        payload = Helper().prepare_payload(None, request.form)
        del payload['name']
        payload['name'] = payload['secret']
        del payload['secret']
        request_data = {'config': {'secrets': {entity: {entity_name: [payload]}}}}
        uri = f'{entity}/{entity_name}'
        response = Rest().post_data('secrets', uri, request_data)

        if response.status_code == 204:
            flash(f'{table.capitalize()}, {payload["name"]} Updated.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('edit', table=return_table, record=record, secret=secret), code=302)
    else:
        return render_template("edit.html", table = table.capitalize(), data=data, entity=entity, entity_name=entity_name, secret_name=secret_name, record=record)


@app.route('/delete/<string:table>/<string:record>/<string:secret>', methods=['GET'])
def delete(table=None, record=None, secret=None):
    """
    This Method will delete a requested record.
    """
    entity = table.replace('secrets', '')
    table = 'secrets'
    entity_name = record
    secret_name = secret
    uri = f'{entity}/{entity_name}/{secret_name}'
    response = Rest().get_delete(table, uri)

    if response.status_code == 204:
        flash(f'{entity_name} secret {secret_name} is deleted.', "success")
    else:
        flash('ERROR :: Something went wrong!', "error")
    return redirect(url_for('home'), code=302)


@app.route('/clone/<string:table>/<string:record>/<string:secret>', methods=['GET', 'POST'])
def clone(table=None, record=None, secret=None):
    """
    This Method will add a requested record.
    """
    data = {}
    return_table = table
    entity = table.replace('secrets', '')
    table = 'secrets'
    entity_name = record
    secret_name = secret
    uri = f'{entity}/{entity_name}/{secret_name}'
    table_data = Rest().get_data(table, uri)
    if isinstance(table_data, dict):
        data = table_data['config'][table][entity][entity_name][0]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
    if request.method == 'POST':
        payload = Helper().prepare_payload(None, request.form)
        del payload['name']
        payload['name'] = payload['secret']
        del payload['secret']
        request_data = {'config': {'secrets': {entity: {entity_name: [payload]}}}}
        uri = f'{entity}/{entity_name}/{secret_name}'

        response = Rest().post_clone('secrets', uri, request_data)

        if response.status_code == 201:
            flash(f'{table.capitalize()}, {payload["name"]} Cloned to {payload["newsecretname"]}.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('clone', table=return_table, record=record, secret=secret), code=302)
    else:
        return render_template("clone.html", table = table.capitalize(), data=data, entity=entity, entity_name=entity_name, secret_name=secret_name)


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
