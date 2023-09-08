#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constant File for the Luna Web.
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2022, Luna2 Project [OOD]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Development"

INI_FILE = '/trinity/local/ondemand/3.0/config/luna.ini'
TOKEN_FILE = '/tmp/token.txt'
LOG_DIR = '/var/log/luna'
LOG_FILE = '/var/log/luna/luna2-web.log'
EDITOR_KEYS = ['options', 'content', 'comment', 'prescript', 'partscript', 'postscript']


def filter_columns(table=None):
    """
    This method remove the unnecessary fields from
    the dataset.
    """
    response = False
    static = {
        'node': ['name', 'group', 'osimage', 'setupbmc', 'bmcsetup', 'status', 'tpm_uuid'],
        'nodeinterface': ['interface', 'ipaddress', 'macaddress', 'network', 'options'],
        'nodesecrets': ['Node', 'name', 'path', 'content']
    }
    response = list(static[table])
    return response


def sortby(table=None):
    """
    This method remove the unnecessary fields from
    the dataset.
    """
    response = False
    static = {
        'node': [
            'name', 'hostname', 'group', 'osimage', 'interfaces', 'status', 'vendor', 'assettag',
            'position', 'switchport', 'setupbmc', 'bmcsetup', 'unmanaged_bmc_users', 'netboot',
            'localinstall', 'bootmenu', 'roles', 'service', 'prescript', 'partscript',
            'postscript','provision_interface', 'provision_method', 'provision_fallback',
            'tpm_uuid', 'tpm_pubkey', 'tpm_sha256', 'comment', 'switch',  'macaddress'
        ],
        'nodeinterface': ['interface', 'ipaddress', 'macaddress', 'network'],
        'nodesecrets': ['Node', 'name', 'path', 'content']
    }
    response = list(static[table])
    return response
