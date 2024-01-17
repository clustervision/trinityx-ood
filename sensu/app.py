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
This is main file. It will create flask object and serve the API's.
"""

__author__      = 'Diego Sonaglia'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Diego Sonaglia'
__email__       = 'diego.sonaglia@clustervision.com'
__status__      = 'Development'


import datetime
from flask import Flask, render_template
from sensu_requests import SensuRequestHandler
from base.config import settings
from utils import prettify_relative_time


app = Flask(__name__, static_url_path='/')
handler = SensuRequestHandler(sensu_url='http://localhost:4567')


@app.route("/")
def index():
    """
    This is main route of application, it will serve index page of the application.
    """
    return render_template('index.html', settings=settings)


@app.route("/checks")
def checks():
    """
    This API will get all the checks.
    """

    items = handler.get_checks()
    current_time = datetime.datetime.utcnow()
    return items
    

@app.route("/events")
def events():
    """
    This API will get all the events.
    """

    items = handler.get_events()
    current_time = datetime.datetime.utcnow()
    return items


@app.template_filter('prettify_ts')
def prettify_ts(timestamp=None):
    """
    This API will get the prettify relative time.
    """
    target_date = datetime.datetime.fromtimestamp(timestamp)
    current_date = datetime.datetime.now()
    delta = (current_date - target_date).seconds
    return prettify_relative_time(delta)


if __name__ == "__main__":
    app.run()
