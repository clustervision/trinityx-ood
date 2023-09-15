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
from flask import Flask, render_template, request
from config import settings
from luna_requests import LunaRequestHandler
"uid","gid","homedir","shell","surname","givenname","phone","email","expire","last_change","password"

app = Flask(__name__, static_url_path='/')
handler = LunaRequestHandler()
fields = {
    'table': {
        'users': ['uid'],
        'groups': ['gid']
    },
    'modal': {
        'users': ['username', "uid", "gid", "homedir", "shell", "surname", "givenname", "phone", "email", "expire", "last_change", "password", 'groups'],
        'groups': ['groupname', 'gid', 'users']
    }
}

@app.route("/")
def index():
    """
    This is main route of application, it will serve index page of the application.
    """
    return render_template('index.html', settings=settings)


@app.route("/modal/<target>/<mode>/<name>")
@app.route("/modal/<target>/<mode>/", defaults={'name': None})
@app.route("/modal/<target>/<mode>", defaults={'name': None})
def modal(target, mode, name):
    """
    This API will get all the users.
    """
    
    if target not in ['users', 'groups']:
        return render_template('base/error.html', message=f'Invalid target {target}, should be either users or groups')
    if mode not in ['create', 'update', 'show']:
        return render_template('base/error.html', message=f'Invalid mode {mode}, should be either create, update or show')
    if mode in ['update', 'show']:
        if name is None:
            return render_template('base/error.html', message=f'Invalid name {name}, should be a valid name')
        item = handler.get(target, name)
    else:
        item = None
    
    all_users = handler.list('users') if target == 'groups' else None
    all_groups = handler.list('groups') if target == 'users' else None
    print(('osusers_modal.html',
                           target,
                           mode,
                           name,
                           item,
                           all_users,
                           all_groups,
                           fields['modal'][target]))
    return render_template('osusers_modal.html',
                           target=target,
                           mode=mode,
                           name=name,
                           item=item,
                           all_users=all_users,
                           all_groups=all_groups,
                           fields=fields['modal'][target])

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


@app.route("/action/<target>/<name>/_<action>", methods=['GET', 'POST'])
@app.route("/action/<target>/_<action>", defaults={'name': None}, methods=['GET', 'POST'])
def action(target, name, action):
    if action not in ['update', 'delete', 'create']:
        return render_template('base/error.html', message=f'Invalid action {action}, should be either update or delete'), 500
    if action in ['update', 'create']:
        data = request.get_json(force=True) or {}
        if target == 'users':
            if 'username' not in data:
                return render_template('base/error.html', message=f'Invalid data {data}, should contain username'), 500
            else:
                name = data.pop('username')
        if target == 'groups':
            if 'groupname' not in data:
                return render_template('base/error.html', message=f'Invalid data {data}, should contain groupname'), 500
            else:
                name = data.pop('groupname')
    else:
        data = {}
    if name is None:
        return render_template('base/error.html', message=f'Invalid name {name}, should be a valid name'), 500

    print(name, data)
    data = {k:(v or None) for k,v in data.items() if k not in ['last_change']}
    try:
        old_data = handler.get(target, name)
        for key, old_value in old_data.items():
            print(key, old_value)
            if data.get(key) == str(old_value):
                data[key] = None
    except:
        pass
    print(name, data)
    try:
        if action == 'delete':
            handler.delete(target, name)
            return render_template('base/success.html', message=f'{target} {name} deleted successfully')
        if action == 'update':
            handler.update(target, name, data)
            return render_template('base/success.html', message=f'{target} {name} updated successfully')
        if action == 'create':
            handler.update(target, name, data)
            return render_template('base/success.html', message=f'{target} created successfully')
    except Exception as e:
        print(e)
        return render_template('base/error.html', message=e), 500

    return '', 200

if __name__ == "__main__":
    app.run()
