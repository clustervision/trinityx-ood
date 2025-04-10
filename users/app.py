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
from flask import Flask, jsonify, render_template, request
from luna_requests import LunaRequestHandler

from base.config import get_configs

CONFIGS = get_configs()

app = Flask(__name__, static_url_path='/')
handler = LunaRequestHandler()
fields = {
    'users': { 
        "uid": {"label": "Username"},
        "cn": {"label": "Common Name"},
        "sn": {"label": "Surname"},
        "givenName": {"label": "Given Name"},
        "uidNumber": {"label": "UID"},
        "gidNumber": {"label": "GID"},
        "homeDirectory": {"label": "Home Directory"},
        "loginShell": {"label": "Login Shell"},
        "telephoneNumber": {"label": "Telephone Number"},
        "mail": {"label": "Email"},
        "shadowExpire": {"label": "Password Expire"},
        "shadowLastChange": {"label": "Last Change"},
        "userPassword": {"label": "Password"},
        'memberOf': {"label": "Groups"},
        },
    'groups': {
        'cn': {},
        'gidNumber': {},
        'member' : {},
        }
    }


@app.template_filter('get_names')
def get_name_filter(items):
    return [i['name'] for i in items]

# add a wrapper to all the routes to catch errors
@app.errorhandler(Exception)
def wrap_errors(error):
    """Decorator to wrap errors in a JSON response."""
    if app.debug:
        raise error
    return jsonify({"message": str(error)}), 500


@app.context_processor
def inject_settings():
    return {"CONFIGS": CONFIGS}


@app.route("/")
def index():
    """
    This is main route of application, it will serve index page of the application.
    """
    return render_template('index.html')

@app.route("/users")
def users():
    """
    This is main route of application, it will serve index page of the application.
    """
    users = handler.list('users')
    return users

@app.route("/groups")
def groups():
    """
    This is main route of application, it will serve index page of the application.
    """
    groups = handler.list('groups')
    return groups



@app.route("/modal/<target>/<mode>/<name>")
@app.route("/modal/<target>/<mode>/", defaults={'name': None})
@app.route("/modal/<target>/<mode>", defaults={'name': None})
def modal(target, mode, name):
    """
    This API will get all the users.
    """
    
    if target not in ['users', 'groups']:
        raise Exception(f'Invalid target {target}, should be either users or groups')
    if mode not in ['create', 'update', 'show', 'delete']:
        raise Exception(f'Invalid mode {mode}, should be either create, update, show or delete')
    if mode in ['update', 'show', 'delete']:
        if name is None:
            raise Exception(f'Invalid name {name}, should be a valid name')
        item = handler.get(target, name)
    else:
        item = None
    
    if mode == 'delete':
        return render_template('osusers_delete_modal.html',
                            target=target,
                            mode=mode,
                            name=name,
                            item=item
                            )

    all_users = handler.list('users') if target == 'groups' else None
    all_groups = handler.list('groups') if target == 'users' else None

    return render_template('osusers_modal.html',
                           target=target,
                           mode=mode,
                           name=name,
                           item=item,
                           all_users=all_users,
                           all_groups=all_groups,
                           fields=fields[target])


@app.route("/action/<target>/<name>/_<action>", methods=['GET', 'POST'])
@app.route("/action/<target>/_<action>", defaults={'name': None}, methods=['GET', 'POST'])
def action(target, name, action):
    if action not in ['update', 'delete', 'create']:
        raise Exception(f'Invalid action {action}, should be either update or delete')
    if action in ['update', 'create']:
        data = request.get_json(force=True) or {}
        if target == 'users':
            if 'uid' not in data:
                raise Exception(f'Invalid data {data}, should contain username')
            else:
                name = data.pop('uid')
        if target == 'groups':
            if 'cn' not in data:
                raise Exception(f'Invalid data {data}, should contain groupname')
            else:
                name = data.pop('cn')
    else:
        data = {}
    if name is None:
        raise Exception(f'Invalid name {name}, should be a valid name')

    data = {k:(v if v != '' else None) for k,v in data.items() if k not in ['shadowLastChange']}
    try:
        old_data = handler.get(target, name)
        for key, old_value in old_data.items():
            if data.get(key) == str(old_value):
                data[key] = None
    except:
        pass


    if action == 'delete':
        handler.delete(target, name)
        return {"message": f'{target} {name} deleted successfully'}
    if action == 'update':
        handler.update(target, name, data)
        return {"message": f'{target} {name} updated successfully'}
    if action == 'create':
        handler.update(target, name, data)
        return {"message": f'{target} created successfully'}


    return '', 200

