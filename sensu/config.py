#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file will create the settings.
"""

__author__      = 'Diego Sonaglia'
__copyright__   = 'Copyright 2022, Luna2 Project[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Diego Sonaglia'
__email__       = 'diego.sonaglia@clustervision.com'
__status__      = 'Development'

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="OOD",
    settings_files=[
        "settings/sensu.toml",
        "/trinity/local/ondemand/3.0/config/sensu.toml",
        ],
)
