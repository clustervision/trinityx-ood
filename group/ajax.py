#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
View, HTTP handler.
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2022, Luna2 Project [WEB]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Development"

import json
from django.http import HttpResponse
from .model import Model
from .log import Log
from .rest import Rest
from .helper import Helper


LOGGER = Log.get_logger()


def get_request(request, status=None, service_name=None, action=None):
    """
    This method will fetch the raw data from the daemon.
    """
    response = {"message": "No Response"}
    if request:
        uri = f'{status}/{service_name}/{action}'
        if action == '_pack':
            uri = f'config/{uri}'
        result = Rest().get_raw(uri)
        response = result.json()
    response = json.dumps(response)
    return HttpResponse(response, content_type="application/json")


def post_request(request, status=None, service_name=None, action=None):
    """
    This method will fetch the raw data from the daemon.
    """
    response = {"message": "No Response"}
    if request.method == "POST":
        data = dict(request.POST)
        if 'csrfmiddlewaretoken' in data:
            del data['csrfmiddlewaretoken']
        hostlist = Helper().collect_nodelist(data['hostlist[]'])
        payload = {status: {service_name: {action: {"hostlist": hostlist}}}}
        uri = f'{status}/{service_name}'
        result = Rest().post_raw(uri, payload)
        response = result.json()
    response = json.dumps(response)
    return HttpResponse(response, content_type="application/json")


def check_status(request, status=None, request_id=None):
    """
    This method will check the status of request on behalf of request ID.
    """
    response = {"message": "No Response"}
    if request:
        uri = f'{status}/status/{request_id}'
        result = Rest().get_raw(uri)
        response = result.json()
    response = json.dumps(response)
    return HttpResponse(response, content_type="application/json")


def get_list(request, table=None):
    """
    This method will return the list of element in table for as option for select tag.
    """
    response = None
    if request:
        response = Model().get_list_options(table)
        response = json.dumps(response)
    return HttpResponse(response, content_type="application/json")


def get_record(request, table=None, record=None):
    """
    This method will return the list of element in table for as option for select tag.
    """
    response = None
    if request:
        response = Model().get_record(table, record)
        response = json.dumps(response)
    return HttpResponse(response, content_type="application/json")
