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

INI_FILE = '/trinity/local/luna/config/luna.ini'
TOKEN_FILE = '/tmp/token.txt'
LOG_DIR = '/var/log/luna'
LOG_FILE = '/var/log/luna/luna2-web.log'

def sortby(table=None):
    """
    This method remove the unnecessary fields from
    the dataset.
    """
    response = False
    static = {
        'cluster': ['name', 'ns_ip','ntp_server', 'provision_fallback', 'provision_method',
                    'security', 'technical_contacts', 'user', 'debug']
    }
    response = list(static[table])
    return response
