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
This File is a Main File AlertX.
This file will provide the functionality to configure and manage the monitoring alerts for nodes.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2025, TrinityX[PASSWD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

import os
from flask import Flask, render_template, request, jsonify
from constant import LICENSE, APP_STATE, TOKEN_FILE
from log import Log
from helper import Helper

LOGGER = Log.init_log('INFO')
app = Flask(__name__, static_folder="static", template_folder="templates")
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
        return render_template("error.html", table='Change Password', data="", error=TOKEN_FILE["error"])
    return None


@app.errorhandler(404)
def page_not_found(e):
    """
    This method will redirect to error Template Page with Error Message on 404.
    """
    return render_template("error.html", table="Change Password", data="", error=f"ERROR :: {e}"), 200


@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application. It will Show Monitor Options.
    """
    return render_template("index.html", table='Change Password')


@app.route('/update_password', methods=['POST'])
def update_password():
    """
    This method will update the password for the user.
    """
    response = {"status": False, "message": "Password Update Failed."}
    if request.method == 'POST':
        request_data = request.json
        old_password = request_data['old_password']
        new_password = request_data['new_password']
        confirm_password = request_data['confirm_password']
        if new_password == confirm_password:
            response = Helper().update_password(old_password, new_password)
        else:
            response = {"status": False, "message": "New Password and Confirm Password should be same."}
    else:
        response = {"status": False, "message": "This method is not supported."}
    return jsonify(response), 200


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
        app.run(host='0.0.0.0', port=7755, debug= True)
    else:
        app.run()
