#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This File is a Main File Luna 2 BMC Setup.
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
    This is the main method of application. It will list all BMC setups which is available with daemon.
    """
    data = ""
    error = ""
    table = 'bmcsetup'
    table_data = Rest().get_data(table)
    logger.info(table_data)
    if table_data:
        raw_data = table_data['config'][table]
        raw_data = Helper().prepare_json(raw_data, True)
        fields, rows  = Helper().filter_data(table, raw_data)
        data = Presenter().show_table(fields, rows)
        data = unescape(data)
    else:
        error = f'No {table.capitalize()} Available at this time.'
    return render_template("inventory.html", table = table.capitalize(), data = data, error = error)


@app.route('/show/<string:record>', methods=['GET'])
def show(record=None):
    """
    This Method will show a specific record.
    """
    data = ""
    error = ""
    table = 'bmcsetup'
    table_data = Rest().get_data(table, record)
    if table_data:
        raw_data = table_data['config'][table][record]
        raw_data = Helper().prepare_json(raw_data)
        fields, rows  = Helper().filter_data_col(table, raw_data)
        data = Presenter().show_table_col(fields, rows)
        data = unescape(data)
    else:
        error = f'{record} From {table.capitalize()} is Not available at this time'
    return render_template("info.html", table = table.capitalize(), data = data, error = error, record=record)


@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    This Method will add a requested record.
    """
    table = 'bmcsetup'
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload = Helper().prepare_payload(None, payload)
        request_data = {'config': {table: {payload['name']: payload}}}
        response = Rest().post_data(table, payload['name'], request_data)
        # response = Helper().add_record(table, request_data)
        if response.status_code == 201:
            flash(f'{table.capitalize()}, {payload["name"]} Created.', "success")
            return redirect(url_for('home'), code=302)
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
            return redirect(url_for('add'), code=302)
    else:
        return render_template("add.html", table = table.capitalize())


@app.route('/edit/<string:record>', methods=['GET', 'POST'])
def edit(record=None):
    """
    This Method will add a requested record.
    """
    data = {}
    table = 'bmcsetup'
    table_data = Rest().get_data(table, record)
    if table_data:
        data = table_data['config'][table][record]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload = Helper().prepare_payload(None, payload)
        request_data = {'config': {table: {payload['name']: payload}}}
        response = Rest().post_data(table, payload['name'], request_data)
        # response = Helper().add_record(table, request_data)
        if response.status_code == 204:
            flash(f'{table.capitalize()}, {payload["name"]} Updated.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('edit', record=record), code=302)
    else:
        return render_template("edit.html", table = table.capitalize(), record = record,  data=data)


@app.route('/delete/<string:record>', methods=['GET'])
def delete(record=None):
    """
    This Method will delete a requested record.
    """
    table = 'bmcsetup'
    response = Rest().get_delete(table, record)
    if response.status_code == 204:
        flash(f'{table.capitalize()}, {record} is deleted.', "success")
    else:
       flash('ERROR :: Something went wrong!', "error")
    return redirect(url_for('home'), code=302)


@app.route('/clone/<string:record>', methods=['GET', 'POST'])
def clone(record=None):
    """
    This Method will clone a requested record.
    """
    data = {}
    table = 'bmcsetup'
    table_data = Rest().get_data(table, record)
    if table_data:
        data = table_data['config'][table][record]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        response = Helper().clone_record(table, payload)
        if response.status_code == 201:
            flash(f'{table.capitalize()}, {data["name"]} Cloned as {payload["name"]}.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('clone', record=record), code=302)
    else:
        return render_template("clone.html", table = table.capitalize(), record = record,  data=data)


@app.route('/member/<string:table>/<string:record>', methods=['GET'])
def member(table=None, record=None):
    """
    This Method will provide all the member nodes for the requested record.
    """
    get_member = Rest().get_data(table, record+'/_list')
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


if __name__ == "__main__":
    # app.run(host= '0.0.0.0', port= 7059, debug= True)
    app.run()
