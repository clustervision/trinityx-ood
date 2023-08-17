#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This File is a Main File Luna 2 Cluster.
This file will create flask object and serve the all routes for on demand.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

from html import unescape
from flask import Flask, json, request, render_template, flash, url_for, redirect
from rest import Rest
from helper import Helper
from presenter import Presenter
from log import Log

logger = Log.init_log('DEBUG')
app = Flask(__name__, static_url_path='/')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application. It will Show Cluster.
    """
    data = ""
    error = ""
    table = 'cluster'
    table_data = Rest().get_data(table)
    logger.info(table_data)
    if table_data:
        raw_data = table_data['config'][table]
        raw_data = Helper().prepare_json(raw_data, True)
        fields, rows  = Helper().filter_data_col(table, raw_data)
        data = Presenter().show_table_col(fields, rows)
        data = unescape(data)
    else:
        error = f'No {table.capitalize()} Available at this time.'
    return render_template("info.html", table = table.capitalize(), data = data, error = error)


@app.route('/rename', methods=['GET', 'POST'])
def rename():
    """
    This method will Rename the Cluster.
    """
    table = 'cluster'
    data = {}
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload['name'] = payload['newname']
        del payload['newname']
        response = Helper().update_record(table, payload)
        if response.status_code == 204:
            flash(f'{table.capitalize()} renamed to {payload["name"]}.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('rename'), code=302)
    elif request.method == 'GET':
        table_data = Rest().get_data(table)
        if table_data:
            raw_data = table_data['config'][table]
            data = {'name': raw_data['name'], 'newname': ''}
    return render_template("rename.html", table = table.capitalize(), data=data)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    """
    This Method will add a requested record.
    """
    data = {}
    table = 'cluster'
    table_data = Rest().get_data(table)
    if table_data:
        data = table_data['config'][table]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        cluster_name = payload['name']
        del payload['name']
        response = Helper().update_record(table, payload)
        # response = Helper().add_record(table, request_data)
        if response.status_code == 204:
            flash(f'{cluster_name} Updated.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('edit'), code=302)
    else:
        return render_template("edit.html", table = table.capitalize(), record = table,  data=data)



if __name__ == "__main__":
    app.run(host= '0.0.0.0', port= 7059, debug= True)
    # app.run()
