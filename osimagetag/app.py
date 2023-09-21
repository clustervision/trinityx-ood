#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This File is a Main File Luna 2 OS Image.
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
from model import Model

LOGGER = Log.init_log('INFO')
TABLE = 'osimagetag'
TABLE_CAP = 'OS Image Tag'
app = Flask(__name__, static_url_path='/')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application.
    It will list all OS Images which is available with daemon.
    """
    data, error = "", ""
    table_data = Rest().get_data("osimagetag")
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config']["osimagetag"]
        raw_data = Helper().prepare_json(raw_data, True)
        fields, rows  = Helper().filter_data("osimagetag", raw_data)
        data = Presenter().show_table(fields, rows)
        data = unescape(data)
    else:
        error = f'No {TABLE_CAP} Available at this time.'
    return render_template("inventory.html", table=TABLE_CAP, data=data, error=error)


@app.route('/show/<string:osimage>', methods=['GET', 'POST'])
def show(osimage=None):
    """
    This Method will show a specific record.
    """
    data, error = "", ""
    table_data = Rest().get_data(TABLE, osimage)
    LOGGER.info(table_data)
    if table_data:
        raw_data = table_data['config'][TABLE]
        raw_data = Helper().prepare_json(raw_data)
        fields, name,  rows  = Helper().filter_data_col(TABLE, raw_data)
        data = Presenter().show_table_col_more_fields(fields, name, rows)
        data = unescape(data)
    else:
        error = f'{osimage} From {TABLE_CAP} is Not available at this time'
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        request_data = {'config': {"osimage": {payload['osimage']: {"tag": payload['tag']}}}}
        response = Rest().post_data("osimage", f"{payload['osimage']}/tag", request_data)
        LOGGER.info(f'{response.status_code} {response.content}')
        if response.status_code == 204:
            flash(f'OS Image Tag {payload["tag"]}, added successfully on {payload["osimage"]}.', "success")
            return redirect(url_for('show', osimage=payload['osimage']), code=302)
    return render_template("info.html", table=TABLE_CAP, data=data, error=error, osimage=osimage)


@app.route('/delete/<string:osimage>/<string:tag>', methods=['GET'])
def delete(osimage=None, tag=None):
    """
    This Method will delete a requested record.
    """
    response = Rest().get_delete("osimage", f'{osimage}/osimagetag/{tag}')
    LOGGER.info(f'{response.status_code} {response.content}')
    if response.status_code == 204:
        flash(f'OS Image Tag {tag}, deleted successfully from {osimage}.', "success")
    else:
        flash('ERROR :: Something went wrong!', "error")
    return redirect(url_for('home'), code=302)


@app.route('/get_record/<string:record>', methods=['GET', 'POST'])
def get_record(record=None):
    """
    This method will return the list of element in table for as option for select tag.
    """
    response = None
    if request:
        response = Model().get_record(TABLE, record)
        response = json.dumps(response)
    return response

if __name__ == "__main__":
    # app.run(host= '0.0.0.0', port= 7059, debug= True)
    app.run()
