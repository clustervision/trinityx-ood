#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This code is part of the TrinityX software suite
# Copyright (C) 2026  ClusterVision Solutions b.v.
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
This Log Class is responsible to start the Logger depend on the Level.
Level alway info until argument --debug is not supplied.
Method get_logger will provide a logging object, which is helpful to write the log messages.
Logger Object have basic methods: debug, error, info, critical and warnings.

"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2026, Luna2 Project [OOD]"
__license__     = "GPL"
__version__     = "3.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Production"

import sys
import logging
from constant import LOG_FILE


class Log:
    """
    This Log Class is responsible to start the Logger depend on the Level.
    """
    __logger = logging.getLogger()


    @classmethod
    def init_log(cls, log_level: str):
        """
        Input - log_level
        Process - Validate the Log Level, Set it to INFO if not correct.
        Output - Logger Object.
        """
        levels = {'NOTSET': 0, 'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
        level = levels[log_level.upper()]
        thread_level = '[%(levelname)s]:[%(asctime)s]:[%(threadName)s]:'
        message = '[%(filename)s:%(funcName)s@%(lineno)d] - %(message)s'
        log_format = f'{thread_level}{message}'
        try:
            logging.basicConfig(filename=LOG_FILE, format=log_format, filemode='a', level=level)
            cls.__logger = logging.getLogger('luna2-cli')
            cls.__logger.setLevel(level)
            if level == 10:
                formatter = logging.Formatter(log_format)
                console = logging.StreamHandler(sys.stdout)
                console.setLevel(level)
                console.setFormatter(formatter)
                cls.__logger.addHandler(console)
            levels = {0:'NOTSET', 10: 'DEBUG', 20: 'INFO', 30: 'WARNING', 40:'ERROR', 50:'CRITICAL'}
            cls.__logger.info("####### Alertx Logging Level IsSet To [%s] ########", levels[level])
            return cls.__logger
        except PermissionError:
            sys.stderr.write('ERROR :: Run this tool as a super user.\n')
            sys.exit(1)


    @classmethod
    def get_logger(cls):
        """
        Input - None
        Output - Logger Object.
        """
        return cls.__logger


    @classmethod
    def check_loglevel(cls):
        """
        Input - None
        Process - Update the existing Log Level
        Output - Logger Object.
        """
        return logging.root.level
