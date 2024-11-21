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


import os
import copy
import yaml
from log import Log
from constant import TRIX_CONFIG, TRIX_CONFIG_DETAILS


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


    def generate_details(self, details=None):
        """
        This method will generate the fresh new detailed file depending on the main file.
        """
        trix_data = ""
        with open(TRIX_CONFIG, 'r') as trix_file:
            trix_data = yaml.safe_load(trix_file)
        
        if trix_data:
            if "groups" in trix_data:
                for groups in trix_data["groups"]:
                    group_rules = groups["rules"]
                    for rule in group_rules:
                        if details is True:
                            rule["labels"]["_trix_status"] = True
                        rule["labels"]["nhc"] = "yes"
        file = TRIX_CONFIG_DETAILS if details is True else TRIX_CONFIG

        self.logger.info(f'Updating File => {file}')
        with open(file, "w") as detail_file:
            yaml.dump(trix_data, detail_file, default_flow_style=False)
        return True


    def check_files(self):
        """
        This method will check both files with read & write permissions, and returns a list of
        errors.
        """
        self.response = []
        for file in [TRIX_CONFIG, TRIX_CONFIG_DETAILS]:
            if os.path.exists(file):
                self.logger.info(f"The file '{file}' exists.")
                if os.access(file, os.R_OK):
                    self.logger.info(f"The file '{file}' is readable.")
                else:
                    self.logger.info(f"The file '{file}' is not readable.")
                    self.response.append(f"The file '{file}' is not readable.")
                if os.access(file, os.W_OK):
                    self.logger.info(f"The file '{file}' is writable.")
                else:
                    self.logger.info(f"The file '{file}' is not writable.")
                    self.response.append(f"The file '{file}' is not writable.")
                if file == TRIX_CONFIG_DETAILS and os.stat(file).st_size == 0:
                    self.logger.info(f"The file '{file}' is empty.")
                    self.generate_details(details=True)
                    self.generate_details(details=False)
                else:
                    self.logger.info(f"The file '{file}' is not empty.")
            else:
                self.logger.info(f"The file '{file}' does not exist.")
                self.response.append(f"The file '{file}' does not exist.")
        return self.response


    def load_yaml(self):
        """
        This method will check the both files rules and detailed, and return the output from the
        detailed file with status.
        """
        self.response = self.check_files()
        if self.response:
            check = False
        else:
            self.logger.info(f'Loading Detailed File => {TRIX_CONFIG_DETAILS}')
            check = True
            with open(TRIX_CONFIG_DETAILS, 'r') as file:
                self.response = yaml.safe_load(file)
        return check, self.response


    def save_configuration(self, json_data=None):
        """
        This method will save the both files rules and detailed, depending on the users validation.
        """
        trix_rules = copy.deepcopy(json_data)
        if trix_rules:
            if "groups" in trix_rules:
                for groups in trix_rules["groups"]:
                    group_rules = groups["rules"]
                    for rule in group_rules:
                        if rule["labels"]["_trix_status"] is False:
                            group_rules.remove(rule)
                        else:
                            del rule["labels"]["_trix_status"]

        self.logger.info(f'Saving Detailed File => {TRIX_CONFIG_DETAILS}')
        with open(TRIX_CONFIG_DETAILS, 'w') as file:
            yaml.dump(json_data, file, default_flow_style=False)
        
        self.logger.info(f'Saving Rules File => {TRIX_CONFIG}')
        with open(TRIX_CONFIG, 'w') as file:
            yaml.dump(trix_rules, file, default_flow_style=False)

        self.response = True
        return self.response
