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
TOKEN_FILE = 'token.txt'
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
        'bmcsetup': ['name', 'userid', 'netchannel', 'mgmtchannel', 'unmanaged_bmc_users'],
        'cluster': ['name', 'hostname','ipaddress', 'technical_contacts', 'provision_method',
                    'security'],
        'controller': ['id', 'clusterid', 'hostname', 'status', 'ipaddress', 'serverport'],
        'group': ['name', 'bmcsetupname', 'osimage', 'provision_fallback', 'interfaces'],
        'groupinterface': ['interface', 'network', 'options'],
        'groupsecrets': ['Group', 'name', 'path', 'content'],
        'ipaddress': ['id', 'ipaddress', 'subnet', 'network'],
        'monitor': ['id', 'nodeid', 'status', 'state'],
        'network': ['name', 'network', 'ns_ip', 'dhcp', 'dhcp_range_begin', 'dhcp_range_end'],
        'node': ['name', 'group', 'osimage', 'setupbmc', 'bmcsetup', 'status', 'tpm_uuid'],
        'nodeinterface': ['interface', 'ipaddress', 'macaddress', 'network', 'options'],
        'nodesecrets': ['Node', 'name', 'path', 'content'],
        'osimage': ['name', 'kernelfile', 'path', 'imagefile', 'distribution', 'osrelease'],
        'otherdev': ['name', 'network', 'ipaddress', 'macaddress', 'comment'],
        'roles': ['id', 'name', 'modules'],
        'switch': ['name', 'network', 'oid', 'read', 'ipaddress'],
        'tracker': ['infohash', 'peer', 'ipaddress', 'port', 'status'],
        'user': ['id', 'username', 'password', 'roleid', 'createdby', 'lastlogin', 'created'],
        'osuser': ['username', 'userid', 'primarygroup', 'groups', 'fullname', 'homedir', 'shell'],
        'osgroup': ['groupname', 'groupid', 'users']
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
        'cluster': ['name', 'ns_ip','ntp_server', 'provision_fallback', 'provision_method',
                    'security', 'technical_contacts', 'user', 'debug'],
        'controller': ['hostname', 'ipaddress','luna_config', 'serverport', 'status'],
        'node': ['name', 'hostname', 'group', 'osimage', 'interfaces', 'localboot',
                    'macaddress', 'switch', 'switchport', 'setupbmc', 'status', 'service',
                    'prescript', 'partscript', 'postscript', 'netboot', 'localinstall',
                    'bootmenu', 'provisionmethod', 'provisioninterface', 'provisionfallback',
                    'tpmuuid', 'tpmpubkey', 'tpmsha256', 'unmanaged_bmc_users', 'comment'],
        'group': ['name', 'bmcsetup', 'bmcsetupname', 'domain', 'interfaces', 'osimage',
                    'prescript', 'partscript', 'postscript', 'netboot', 'localinstall',
                    'bootmenu', 'provisionmethod', 'provisioninterface', 'provisionfallback',
                    'unmanaged_bmc_users','comment'],
        'bmcsetup': ['name', 'userid', 'username', 'password', 'netchannel', 'mgmtchannel',
                        'unmanaged_bmc_users', 'comment'],
        'osimage': ['name', 'dracutmodules', 'grab_filesystems', 'grab_exclude', 'initrdfile',
                    'kernelversion', 'kernelfile', 'kernelmodules', 'kerneloptions', 'path',
                    'imagefile', 'distribution', 'osrelease', 'comment'],
        'switch': ['name', 'network', 'oid', 'read', 'rw', 'ipaddress', 'comment'],
        'otherdev': ['name', 'network', 'ipaddress', 'macaddress', 'comment'],
        'nodeinterface': ['interface', 'ipaddress', 'macaddress', 'network'],
        'groupinterface': ['interfacename', 'network'],
        'groupsecrets': ['Group', 'name', 'path', 'content'],
        'nodesecrets': ['Node', 'name', 'path', 'content'],
        'network': ['name', 'network', 'ns_hostname', 'ns_ip', 'ntp_server', 'gateway', 'dhcp',
                    'dhcp_range_begin', 'dhcp_range_end', 'comment'],
        'system': ['Architecture', 'Machine', 'Release', 'Version', 'Platform', 'Processor']
    }
    response = list(static[table])
    return response
