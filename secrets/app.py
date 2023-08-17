#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This File is a Main File Luna 2 Secrets.
This file will create flask object and serve the all routes for on demand.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'


import json
from string import Template
from html import unescape
from flask import Flask,request, render_template, flash, url_for, redirect
from rest import Rest
from helper import Helper
from presenter import Presenter
from log import Log
from model import Model

logger = Log.init_log('DEBUG')
app = Flask(__name__, static_url_path='/')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/', methods=['GET'])
@app.route('/<string:entity>', methods=['GET'])
def home(entity=None):
    """
    This is the main method of application. It will list all Secrets which is available with daemon.
    """
    table = 'secrets'
    secrets = True
    group_secrets, node_secrets = '', ''
    record=None
    secret=None
    uri = 'secrets'
    if record:
        uri = f'{uri}/{entity}/{record}'
        if secret:
            uri = f'{uri}/{secret}'
    secret_list = Rest().get_data(uri)
    if secret_list:
        secret_data = secret_list['config']['secrets']
        if 'group' in secret_data:
            fields, rows  =  Helper().get_secrets('groupsecrets', secret_data['group'])
            group_secrets = Presenter().show_table(fields, rows)
            group_secrets = unescape(group_secrets)
        if 'node' in secret_data:
            fields, rows  =  Helper().get_secrets('nodesecrets', secret_data['node'])
            node_secrets = Presenter().show_table(fields, rows)
            node_secrets = unescape(node_secrets)
    else:
        flash('Secrets are not available.', 'error')
        secrets = False
    if entity:
        if entity == 'group':
            node_secrets = ''
        if entity == 'node':
            group_secrets = ''

    return render_template("inventory.html", table = table.capitalize(), secrets=secrets, group_secrets=group_secrets, node_secrets=node_secrets)


# def secrets(request, table=None, record=None, secret=None):
#     """
#     This method will open the Login Page(First Page)
#     """
#     if 'username' not in request.session:
#         return HttpResponseRedirect("/")
#     context = {"table": 'Secrets', 'secrets': True, "daemon_status": Helper().daemon_status()}
#     group_secrets, node_secrets = '', ''
#     uri = 'secrets'
#     if record:
#         uri = f'{uri}/{table}/{record}'
#         if secret:
#             uri = f'{uri}/{secret}'
#     secret_list = Rest().get_data(uri)
#     if secret_list:
#         secret_data = secret_list['config']['secrets']
#         if 'group' in secret_data:
#             fields, rows  =  Helper().get_secrets('groupsecrets', secret_data['group'])
#             group_secrets = Presenter().show_table(fields, rows)
#             group_secrets = unescape(group_secrets)
#         if 'node' in secret_data:
#             fields, rows  =  Helper().get_secrets('nodesecrets', secret_data['node'])
#             node_secrets = Presenter().show_table(fields, rows)
#             node_secrets = unescape(node_secrets)
#     else:
#         flash('Secrets are not available.', 'error')
#         context['secrets'] = False
#     if table:
#         if table == 'group':
#             context['group_secrets'] = group_secrets
#         if table == 'node':
#             context['node_secrets'] = node_secrets
#     else:
#         context['group_secrets'] = group_secrets
#         context['node_secrets'] = node_secrets

#     template = loader.get_template("inventory.html")
#     return HttpResponse(template.render(context, request))



@app.route('/show/<string:record>', methods=['GET'])
def show(record=None):
    """
    This Method will show a specific record.
    """
    data = ""
    error = ""
    table = 'node'
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


@app.route('/get_list/<string:table>', methods=['GET', 'POST'])
def get_list(table=None):
    """
    This method will return the list of element in table for as option for select tag.
    """
    response = None
    if request:
        response = Model().get_list_options(table)
        response = json.dumps(response)
    return response



@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    This Method will add a requested record.
    """
    table = 'node'
    group_list = Model().get_list_option_html('group')
    bmcsetup_list = Model().get_list_option_html('bmcsetup')
    osimage_list = Model().get_list_option_html('osimage')
    network_list = Model().get_list_option_html('network')
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload = Helper().prepare_payload(None, payload)
        for k, v in payload.items():
            if v == 'on':
                payload[k] = True

        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, table, payload)
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
        return render_template("add.html", table = table.capitalize(), bmcsetup_list=bmcsetup_list, osimage_list=osimage_list, network_list=network_list, group_list=group_list)


@app.route('/edit/<string:record>', methods=['GET', 'POST'])
def edit(record=None):
    """
    This Method will add a requested record.
    """
    data = {}
    table = 'node'
    table_data = Rest().get_data(table, record)
    if table_data:
        data = table_data['config'][table][record]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
        if 'bmcsetupname' in data:
            bmcsetup_list = Model().get_list_option_html('bmcsetup', data['bmcsetupname'])
        else:
            bmcsetup_list = Model().get_list_option_html('bmcsetup')
        if 'osimage' in data:
            osimage_list = Model().get_list_option_html('osimage', data['osimage'])
        else:
            osimage_list = Model().get_list_option_html('osimage')
        if 'group' in data:
            group_list = Model().get_list_option_html('group', data['group'])
        else:
            group_list = Model().get_list_option_html('group')

        raw_html = Template("""
            <div class="input-group">
                <span class="input-group-text">Interface</span>
                <input type="text" name="interface" class="form-control" maxlength="100" id="id_interface" value="$interface" />
                <span class="input-group-text">Ip address</span>
                <input type="text" name="ipaddress" class="form-control ipv4" maxlength="100" id="id_ipaddress" inputmode="decimal" value="$ipaddress" />
                <span class="input-group-text">Mac address</span>
                <input type="text" name="macaddress" class="form-control mac" maxlength="100" id="id_macaddress" inputmode="text" value="$macaddress" />
                <span class="input-group-text">Network</span>
                <select name="network" class="form-control" id="id_network">$network</select>
                <span class="input-group-text">Options</span>
                <input type="text" name="options" class="form-control" maxlength="100" id="id_options" value="$options" />
                $button
              </div><br />""")
        interface_html = ""
        add_button = '<button type="button" id="add_nodeinterface" class="btn btn-sm btn-warning">Add Interface</button>'
        remove_button = '<button type="button" class="btn btn-sm btn-danger" id="remove_nodeinterface">Remove Interface</button>'
        if 'interfaces' in data:
            num = 0
            for interface_dict in data['interfaces']:
                interface = interface_dict['interface'] if 'interface' in interface_dict else ""
                ipaddress = interface_dict['ipaddress'] if 'ipaddress' in interface_dict else ""
                macaddress = interface_dict['macaddress'] if 'macaddress' in interface_dict else ""
                macaddress = "" if macaddress == None else macaddress
                network = Model().get_list_option_html('network', interface_dict['network']) if 'network' in interface_dict else ""
                options = interface_dict['options'] if 'options' in interface_dict else ""
                if num == 0:
                    interface_html += raw_html.safe_substitute(interface=interface, ipaddress=ipaddress, macaddress=macaddress, network=network, options=options, button=add_button)
                else:
                    interface_html += raw_html.safe_substitute(interface=interface, ipaddress=ipaddress, macaddress=macaddress, network=network, options=options, button=remove_button)
                num = num + 1
        else:
            interface_html = raw_html.safe_substitute(interface='', network=Model().get_list_option_html('network'), options='', button=add_button)
        interface_html = interface_html[:-6]
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload = Helper().prepare_payload(None, payload)
        for k, v in payload.items():
            if v == 'on':
                payload[k] = True

        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, table, payload)
        request_data = {'config': {table: {payload['name']: payload}}}
        response = Rest().post_data(table, payload['name'], request_data)
        if response.status_code == 204:
            flash(f'{table.capitalize()}, {payload["name"]} Updated.', "success")
        else:
            response_json = response.json()
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('edit', record=record), code=302)
    else:
        return render_template("edit.html", table = table.capitalize(), record = record,  data=data, bmcsetup_list=bmcsetup_list, osimage_list=osimage_list, interface_html=interface_html, group_list=group_list)


@app.route('/delete/<string:record>', methods=['GET'])
def delete(record=None):
    """
    This Method will delete a requested record.
    """
    table = 'node'
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
    table = 'node'
    table_data = Rest().get_data(table, record)
    if table_data:
        data = table_data['config'][table][record]
        data = {k: v for k, v in data.items() if v not in [None, '', 'None']}
        data = Helper().prepare_json(data)
        if 'bmcsetupname' in data:
            bmcsetup_list = Model().get_list_option_html('bmcsetup', data['bmcsetupname'])
        else:
            bmcsetup_list = Model().get_list_option_html('bmcsetup')
        if 'osimage' in data:
            osimage_list = Model().get_list_option_html('osimage', data['osimage'])
        else:
            osimage_list = Model().get_list_option_html('osimage')
        if 'group' in data:
            group_list = Model().get_list_option_html('group', data['group'])
        else:
            group_list = Model().get_list_option_html('group')
        raw_html = Template("""
            <div class="input-group">
                <span class="input-group-text">Interface</span>
                <input type="text" name="interface" class="form-control" maxlength="100" id="id_interface" value="$interface" />
                <span class="input-group-text">Ip address</span>
                <input type="text" name="ipaddress" class="form-control ipv4" maxlength="100" id="id_ipaddress" inputmode="decimal" value="$ipaddress" />
                <span class="input-group-text">Mac address</span>
                <input type="text" name="macaddress" class="form-control mac" maxlength="100" id="id_macaddress" inputmode="text" value="$macaddress" />
                <span class="input-group-text">Network</span>
                <span class="input-group-text">Network</span>
                <select name="network" class="form-control" id="id_network">$network</select>
                <span class="input-group-text">Options</span>
                <input type="text" name="options" class="form-control" maxlength="100" id="id_options" value="$options" />
                $button
              </div><br />""")
        interface_html = ""
        add_button = '<button type="button" id="add_nodeinterface" class="btn btn-sm btn-warning">Add Interface</button>'
        remove_button = '<button type="button" class="btn btn-sm btn-danger" id="remove_nodeinterface">Remove Interface</button>'
        if 'interfaces' in data:
            num = 0
            for interface_dict in data['interfaces']:
                interface = interface_dict['interface'] if 'interface' in interface_dict else ""
                ipaddress = interface_dict['ipaddress'] if 'ipaddress' in interface_dict else ""
                macaddress = interface_dict['macaddress'] if 'macaddress' in interface_dict else ""
                macaddress = "" if macaddress == None else macaddress
                network = Model().get_list_option_html('network', interface_dict['network']) if 'network' in interface_dict else ""
                options = interface_dict['options'] if 'options' in interface_dict else ""
                if num == 0:
                    interface_html += raw_html.safe_substitute(interface=interface, ipaddress=ipaddress, macaddress=macaddress, network=network, options=options, button=add_button)
                else:
                    interface_html += raw_html.safe_substitute(interface=interface, ipaddress=ipaddress, macaddress=macaddress, network=network, options=options, button=remove_button)
                num = num + 1
        else:
            interface_html = raw_html.safe_substitute(interface='', network=Model().get_list_option_html('network'), options='', button=add_button)
        interface_html = interface_html[:-6]
    if request.method == 'POST':
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        payload = Helper().prepare_payload(None, payload)
        for k, v in payload.items():
            if v == 'on':
                payload[k] = True

        if 'interface' in payload:
            payload = Helper().filter_interfaces(request, table, payload)
        request_data = {'config': {table: {payload['name']: payload}}}
        response = Rest().post_clone(table, payload['name'], request_data)
        if response.status_code == 201:
            flash(f'{table.capitalize()}, {data["name"]} Cloned as {payload["name"]}.', "success")
        else:
            try:
                response_json = response.json()
                error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            except json.decoder.JSONDecodeError:
                error = f'HTTP ERROR :: {response.status_code} - {response.content}'
            flash(error, "error")
        return redirect(url_for('clone', record=record), code=302)
    else:
        return render_template("clone.html", table = table.capitalize(), record = record,  data=data, bmcsetup_list=bmcsetup_list, osimage_list=osimage_list, interface_html=interface_html, group_list=group_list)


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


@app.route('/osgrab/<string:record>', methods=['GET', 'POST'])
def osgrab(record=None):
    """
    This method will open the Login Page(First Page)
    """
    table = 'node'
    data = {}
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        request_data = {'config':{table:{payload['name']: payload}}}
        uri = f'config/{table}/{payload["name"]}/_osgrab'
        response = Rest().post_raw(uri, request_data)
        response_json = response.json()
        if response.status_code == 200:
            flash(response_json['message'], "success")
            if 'request_id' in response_json:
                return redirect(url_for('osgrab', record = record, request_id=response_json['request_id'], message=response_json['message']), code=302)
        else:
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('osgrab', record=record), code=302)

    elif request.method == 'GET':
        table_data = Rest().get_data(table, record)
        node_list = Model().get_list_option_html('node', record)
        if table_data:
            raw_data = table_data['config'][table][record]
            data = Helper().prepare_json(raw_data)
            osimage_list = Model().get_list_option_html('osimage', data['osimage'])
    return render_template("osgrab.html", table = table.capitalize(), record = record,  data=data, node_list=node_list, osimage_list=osimage_list)



@app.route('/ospush/<string:record>', methods=['GET', 'POST'])
def ospush(record=None):
    """
    This method will open the Login Page(First Page)
    """
    table = 'node'
    data = {}
    if request.method == "POST":
        payload = {k: v for k, v in request.form.items() if v not in [None, '']}
        request_data = {'config':{table:{payload['name']: payload}}}
        uri = f'config/{table}/{payload["name"]}/_ospush'
        response = Rest().post_raw(uri, request_data)
        response_json = response.json()
        if response.status_code == 200:
            flash(response_json['message'], "success")
            if 'request_id' in response_json:
                return redirect(url_for('ospush', record = record, request_id=response_json['request_id'], message=response_json['message']), code=302)
        else:
            error = f'HTTP ERROR :: {response.status_code} - {response_json["message"]}'
            flash(error, "error")
        return redirect(url_for('ospush', record=record), code=302)

    elif request.method == 'GET':
        table_data = Rest().get_data(table, record)
        node_list = Model().get_list_option_html('node', record)
        if table_data:
            raw_data = table_data['config'][table][record]
            data = Helper().prepare_json(raw_data)
            osimage_list = Model().get_list_option_html('osimage', data['osimage'])
    return render_template("ospush.html", table = table.capitalize(), record = record,  data=data, node_list=node_list, osimage_list=osimage_list)


@app.route('/check_status/<string:status>/status/<string:request_id>', methods=['GET'])
def check_status(status=None, request_id=None):
    """
    This method will check the status of request on behalf of request ID.
    """
    response = {"message": "No Response"}
    if request:
        uri = f'{status}/status/{request_id}'
        result = Rest().get_raw(uri)
        response = result.json()
    response = json.dumps(response)
    return response


if __name__ == "__main__":
    app.run(host= '0.0.0.0', port= 7059, debug= True)
    # app.run()
