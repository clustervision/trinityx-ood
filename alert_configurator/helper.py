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
Helper Class for the Luna WEB
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2022, Luna2 Project [WEB]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Development"

import yaml
from log import Log
from constant import TRIX_CONFIG


class Helper():
    """
    All kind of helper methods.
    """

    def __init__(self):
        """
        Constructor - As of now, nothing have to initialize.
        """
        self.logger = Log.get_logger()
        self.response = None


    def load_yaml(self):
        """
        This method will generate the data as for
        row format from the interface
        """
        self.logger.debug(f'Trix Config File => {TRIX_CONFIG}')
        with open(TRIX_CONFIG, 'r') as file:
            self.response = yaml.safe_load(file)
        return self.response


    def json_to_yaml(self, json_data=None):
        """
        This method will generate the data as for
        row format from the interface
        """
        self.logger.debug(f'JSON Data => {json_data}')
        self.response = yaml.dump(json_data, default_flow_style=False)
        return self.response


    def save_configuration(self, yaml_data=None):
        """
        This method will generate the data as for
        row format from the interface
        """
        self.logger.debug(f'Trix Config File => {TRIX_CONFIG}')
        with open(TRIX_CONFIG, 'w') as file:
            yaml.dump(yaml_data, file, default_flow_style=False)
            self.response = True
        return self.response
