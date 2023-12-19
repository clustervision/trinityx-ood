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
This File is a Main File Luna 2 Monitor.
This file will provide the functionality to observe the Luna status and queue.
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
from flask import Flask, render_template
from rest import Rest
from constant import LICENSE
from log import Log
from helper import Helper
from presenter import Presenter

LOGGER = Log.init_log('INFO')
TABLE = 'monitor'
TABLE_CAP = 'Monitor'
app = Flask(__name__, static_url_path='/')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/', methods=['GET'])
def home():
    """
    This is the main method of application. It will Show Monitor Options.
    """

    """
    API - URI -> /config/rack
    API - URI -> /config/rack/rack001
    Method -  GET & POST [on GET get the data; on POST Create OR Update]
    """
    rack_data = {
         "config": {
            "rack": {
                "rack001": {"size": 52, "devices": [{"name": "node001", "type": "compute", "height": 1, "postion": 1}, {"name": "node002", "type": "compute", "height": 2, "postion": 5}, {"name": "node003", "type": "compute", "height": 3, "postion": 11}, {"name": "switch001", "type": "switch", "height": 4, "postion": 20}, ] },
                "rack002": {"size": 42, "devices": [{"name": "node004", "type": "compute", "height": 5, "postion": 1}, {"name": "node005", "type": "compute", "height": 6, "postion": 6}, {"name": "node006", "type": "compute", "height": 7, "postion": 15}, {"name": "switch002", "type": "switch", "height": 8, "postion": 25}, ] },
                "rack003": {"size": 48, "devices": [{"name": "node007", "type": "compute", "height": 5, "postion": 1}, {"name": "node008", "type": "compute", "height": 4, "postion": 5}, {"name": "node009", "type": "compute", "height": 4, "postion": 11}, {"name": "switch003", "type": "switch", "height": 2, "postion": 20}, ] },
                "rack004": {"size": 50, "devices": [{"name": "node010", "type": "compute", "height": 1, "postion": 1}, {"name": "node011", "type": "compute", "height": 1, "postion": 5}, {"name": "node012", "type": "compute", "height": 4, "postion": 11}, {"name": "switch004", "type": "switch", "height": 2, "postion": 20}, ] },
                "rack005": {"size": 30, "devices": [{"name": "node013", "type": "compute", "height": 1, "postion": 1}, {"name": "node014", "type": "compute", "height": 1, "postion": 5}, {"name": "node015", "type": "compute", "height": 4, "postion": 11}, {"name": "switch005", "type": "switch", "height": 2, "postion": 20}, ] }
            }
        }
    }

    """
    API - URI -> /config/rack/inventory
    Method -  GET & POST [on GET get the data; on POST Create OR Update]
    """
    inventory = {
        "config": {
            "rack": {
                "inventory": [
                    {"name": "node00111", "type": "compute", "height": 1}, {"name": "node00211", "type": "compute", "height": 2}, {"name": "node00311", "type": "compute", "height": 3}, {"name": "switch00111", "type": "switch", "height": 4}, 
                    {"name": "node00411", "type": "compute", "height": 5}, {"name": "node00511", "type": "compute", "height": 6}, {"name": "node00611", "type": "compute", "height": 7}, {"name": "switch00211", "type": "switch", "height": 8}, 
                    {"name": "node00711", "type": "compute", "height": 1}, {"name": "node00811", "type": "compute", "height": 1}, {"name": "node00911", "type": "compute", "height": 4}, {"name": "switch00311", "type": "switch", "height": 2}, 
                    {"name": "node01011", "type": "compute", "height": 1}, {"name": "node01111", "type": "compute", "height": 1}, {"name": "node01211", "type": "compute", "height": 4}, {"name": "switch00411", "type": "switch", "height": 2}, 
                    {"name": "node01311", "type": "compute", "height": 1}, {"name": "node01411", "type": "compute", "height": 1}, {"name": "node01511", "type": "compute", "height": 4}, {"name": "switch00511", "type": "switch", "height": 2},
                ]
            }
        }
    }

    """
    API - URI -> /config/rack/rack001/_delete
    Method -  GET [Delete the Rack From Database, Move devices into the inventory]
    API - URI -> /config/rack/inventory/node00111/_delete
    Method -  GET & DELETE [Delete device from the inventory ]
    """

    rack_data = rack_data["config"]["rack"]
    inventory = inventory["config"]["rack"]["inventory"]
    

    # response = status('status')
    return render_template("monitor.html", table=TABLE_CAP, rack_data=rack_data, inventory=inventory, rack_size=52, title='Status')
    # return render_template("newrack.html", table=TABLE_CAP, rack_data=rack_data, data=response, title='Status')


@app.route('/status/<string:service>', methods=['GET'])
def status(service=None):
    """
    This method to show the monitor status and queue.
    """
    response = ''
    data = Rest().get_raw('monitor', service)
    if data.content:
        data = data.content.decode("utf-8")
        data = json.loads(data)
        data = data['monitor'][service]
        if data:
            fields, rows  = Helper().filter_interface(service, data)
            fields = list(map(lambda x: x.replace('username_initiator', 'Initiate By'), fields))
            fields = list(map(lambda x: x.replace('request_id', 'Request ID'), fields))
            fields = list(map(lambda x: x.replace('read', 'Read'), fields))
            fields = list(map(lambda x: x.replace('message', 'Message'), fields))
            fields = list(map(lambda x: x.replace('created', 'Created On'), fields))
            fields = list(map(lambda x: x.replace('username_initiator', 'Initiate By'), fields))
            fields = list(map(lambda x: x.replace('level', 'Level'), fields))
            fields = list(map(lambda x: x.replace('status', 'Status'), fields))
            fields = list(map(lambda x: x.replace('subsystem', 'Sub System'), fields))
            fields = list(map(lambda x: x.replace('task', 'Task'), fields))
            data = Presenter().show_table(fields, rows)
            response = unescape(data)
        else:
            response = f'<center><strong style="color: blue;">Monitor {service} is empty.</strong></center>'
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
    app.run(host= '0.0.0.0', port= 7059, debug= True)
    # app.run()
