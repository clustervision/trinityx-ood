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
This File is a Main File Luna 2 Network.
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
from constant import LICENSE, filter_columns, TOKEN_FILE, APP_STATE
from helper import Helper
from presenter import Presenter
from log import Log
from model import Model

LOGGER = Log.init_log('INFO')
TABLE = 'dns'
TABLE_CAP = 'DNS'
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
    This is the main method of application. It will list all DNS Records which is available with daemon.
    """
    data, error = "", ""
    dns_records = []
    networks = Model().get_name_list('network')
    if networks:
        for each in networks:
            dns_data = Rest().get_data(TABLE, each)
            if isinstance(dns_data, dict):
                dns_data = dns_data['config']['dns'][each]
                for entry in dns_data:
                    edit_host =  Helper().make_icon(
                        href=url_for('edit', network=each, host=entry['host']),
                        onclick=None,
                        text=f'Change {entry["host"]} with Network {each}',
                        icon='bx-edit',
                        color='#696cff;'
                    )
                    delete_host =  Helper().make_icon(
                        href=url_for('delete', network=each, host=entry['host']),
                        onclick=f'return confirm(\'Are you sure you want to delete {entry["host"]} from {each}?\');',
                        text=f'Delete {entry["host"]} from {each}',
                        icon='bx-trash',
                        color='red;'
                    )
                    dns_records.append([each, entry['host'], entry['ipaddress'], f'{edit_host}{delete_host}'])
    fields = filter_columns(TABLE)
    fields.insert(0, '#')
    if dns_records:
        num = 1
        for outer in dns_records:
            outer.insert(0, num)
            num = num + 1
        data = Presenter().show_table(fields, dns_records)
        data = unescape(data)
    return render_template("inventory.html", table=TABLE_CAP, data=data, error=error)


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
        request_data = {
            'config': {
                TABLE: {
                    payload['network']: [{'host': payload['host'], 'ipaddress': payload['ipaddress']}]
                }
            }
        }
        response = Rest().post_data(TABLE, payload['network'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 201:
            flash(f'{payload["network"]}, {payload["host"]} is Added with {payload["ipaddress"]}.', "success")
            return redirect(url_for('home'), code=302)
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
            return redirect(url_for('add'), code=302)
    else:
        return render_template("add.html", table=TABLE_CAP, network_list=network_list, page=page)



@app.route('/edit/<string:network>/<string:host>', methods=['GET', 'POST'])
def edit(network=None, host=None):
    """
    This Method will add a requested record.
    """
    ipaddress = ''
    network_list = Model().get_list_options('network', network)
    dns_data = Rest().get_data(TABLE, network)
    if dns_data:
        dns_data = dns_data['config']['dns'][network]
        for entry in dns_data:
            if host == entry['host']:
                ipaddress = entry['ipaddress']
        if ipaddress:
            data = {'network': network, 'host': host, 'ipaddress': ipaddress}
        else:
            data = {}
    else:
        data = {}
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        request_data = {
            'config': {
                TABLE: {
                    payload['network']: [{'host': payload['host'], 'ipaddress': payload['ipaddress']}]
                }
            }
        }
        response = Rest().post_data(TABLE, payload['network'], request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 201:
            flash(f'{payload["network"]}, {payload["host"]} is Updated with {payload["ipaddress"]}.', "success")
            return redirect(url_for('edit', network=payload["network"], host=payload["host"]), code=302)
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
            return redirect(url_for('edit', network=payload["network"], host=payload["host"]), code=302)
    else:
        return render_template("edit.html", table=TABLE_CAP, record=network, host=host,  data=data, network_list=network_list)


@app.route('/delete/<string:network>/<string:host>', methods=['GET'])
def delete(network=None, host=None):
    """
    This Method will delete a requested record.
    """
    response = Rest().get_delete(TABLE, f'{network}/{host}')
    if response.status_code == 204:
        flash(f'{host} entry  is deleted from network {network}.', "success")
    else:
        flash('ERROR :: Something went wrong!', "error")
    return redirect(url_for('home'), code=302)


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
