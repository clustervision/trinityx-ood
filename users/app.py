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
fields = {
    'table': {
        'users': ['username', 'uid', ],
        'groups': ['groupname', 'gid',]
    },
    'modal': {
        'users': ['username', 'surname', 'givenname', 'email', 'phone', 'shell', 'homedir', 'expire', 'last_change', 'group', 'groups', 'password'],
        'groups': ['groupname', 'gid', 'users']
    }
}

@app.route("/")
def index():
    """
    This is main route of application, it will serve index page of the application.
    """
    return render_template('index.html', settings=settings)

@app.route("/modal/<target>/<mode>", defaults={'name': None})
@app.route("/modal/<target>/<mode>/<name>")
def modal(target, mode, name):
    """
    This API will get all the users.
    """
    if target not in ['users', 'groups']:
        return render_template('base/error.html', message=f'Invalid target {target}, should be either users or groups')
    if mode not in ['create', 'update', 'show']:
        return render_template('base/error.html', message=f'Invalid mode {mode}, should be either create, update or show')
    if mode in ['update', 'show'] and name is None:
        return render_template('base/error.html', message=f'Invalid name {name}, should be a valid name')
    return render_template('osusers_modal.html', target=target, mode=mode, name=name, fields=fields['modal'][target])

@app.route("/table/<target>")
def table(target):
    """
    This API will get all the users.
    """
    if target not in ['users', 'groups']:
        return render_template('base/error.html', message=f'Invalid target {target}, should be either users or groups')
    try:
        items = handler.list(target)
        current_time = datetime.datetime.utcnow()
        return render_template('osusers_table.html', target=target, fields=fields['table'][target], items=items, time=current_time)
    except Exception as e:
        return render_template('base/error.html', message=e)

if __name__ == "__main__":
    app.run()
