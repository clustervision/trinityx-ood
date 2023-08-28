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
from flask import Flask, render_template
from config import settings
from luna_requests import LunaRequestHandler

app = Flask(__name__, static_url_path='/')
handler = LunaRequestHandler()

@app.route("/")
def index():
    """
    This is main route of application, it will serve index page of the application.
    """
    return render_template('index.html', refresh_interval=settings.luna.refresh_interval)

@app.route("/users")
def users():
    """
    This API will get all the users.
    """
    try:
        items = handler.get_users()
        current_time = datetime.datetime.utcnow()
        return render_template('users_table.html', items=items, time=current_time)
    except Exception as e:
        return render_template('base/error.html', message=e)
    
@app.route("/groups")
def groups():
    """
    This API will get all the groups.
    """
    try:
        items = handler.get_groups()
        current_time = datetime.datetime.utcnow()
        return render_template('groups_table.html', items=items, time=current_time)
    except Exception as e:
        return render_template('base/error.html', message=e)

if __name__ == "__main__":
    app.run()
