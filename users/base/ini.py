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


import os, sys
from configparser import RawConfigParser

class Ini:
    """
    This Ini Class is responsible for reading and parsing the luna.ini file.
    """

    @classmethod
    def get_option(ini, parser=None, errors=None,  section=None, option=None):
        """
        This method will retrieve the value from the INI section
        """
        response = False
        if parser.has_option(section, option):
            response = parser.get(section, option)
        else:
            errors.append(f'{option} is not found in section {section}')
        return response, errors


    @classmethod
    def read_ini(ini, ini_file=None):
        config, errors = {}, []
        username, password, daemon, secret_key, protocol, security = None, None, None, None, None, ''
        file_check = os.path.isfile(ini_file)
        read_check = os.access(ini_file, os.R_OK)
        if file_check and read_check:
            configparser = RawConfigParser()
            configparser.read(ini_file)
            if configparser.has_section('API'):
                for item in ['username','password','protocol','endpoint']:
                    config[item.upper()], errors = ini.get_option(configparser, errors,  'API', item.upper())
                secret_key, _ = ini.get_option(configparser, errors,  'API', 'SECRET_KEY')
                security, _ = ini.get_option(configparser, errors,  'API', 'VERIFY_CERTIFICATE')
                config["VERIFY_CERTIFICATE"] = True if security.lower() in ['y', 'yes', 'true']  else False
            else:
                errors.append(f'API section is not found in {ini_file}.')
        else:
            errors.append(f'{ini_file} is not found on this machine.')
        if errors:
            sys.stderr.write('You need to fix following errors...\n')
            num = 1
            for error in errors:
                sys.stderr.write(f'{num}. {error}\n')
            sys.exit(1)
        return config
