#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from flask import Flask, render_template, redirect, request
from sensu_requests import SensuRequestHandler
from config import sensu_settings
from utils import prettify_relative_time


app = Flask(__name__, static_url_path='/')
handler = SensuRequestHandler(sensu_settings=sensu_settings)


@app.route("/")
def index():
    """
    This is main route of application, it will serve index page of the application.
    """
    return render_template('index.html', sensu_settings=sensu_settings)


@app.route("/checks")
def checks():
    """
    This API will get all the checks.
    """
    items = handler.get_checks()
    current_time = datetime.datetime.utcnow()
    return render_template('checks_table.html', items=items, time=current_time)


@app.route("/events")
def events():
    """
    This API will get all the events.
    """
    items = handler.get_events()
    current_time = datetime.datetime.utcnow()
    return render_template('events_table.html', items=items, time=current_time)


@app.route("/silenced")
def silenced():
    """
    This API will get all the silenced.
    """
    items = handler.get_silenced()
    current_time = datetime.datetime.utcnow()
    return render_template('silenced_table.html', items=items, time=current_time)


@app.route("/dashboard")
def dashboard():
    """
    This API will show the dashboard.
    - Kind of a hacky workaround to get the dashboard url
    """
    if sensu_settings.ood_use_tls:
        schema = 'https'
    else:
        schema = 'http'
    return redirect(f"{schema}://{request.host}")


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
