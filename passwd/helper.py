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
Helper Class for the AlertX.
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2025, TrinityX[PASSWD]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Development"

# import os
import sys
import pexpect
# from urllib.parse import urlparse, urlunparse
# from flask import url_for
# from constant import APP_STATE, ALERT_MANAGER_DIR
from log import Log


class Helper():
    """
    All kind of helper methods.
    """

    def __init__(self):
        """
        Constructor - As of now, nothing have to initialize.
        """
        self.logger = Log.get_logger()


    def update_password(self, old_password=None, new_password=None):
        """
        This method will provide the URL's for the frontend application.
        """
        response = {"status": False, "message": "Password Update Failed."}
        cur_password = old_password
        child = pexpect.spawnu('/usr/bin/passwd') ########### Only for Testing Purpose Sumit@clustervision12
        child.expect('[Cc]urrent [Pp]assword:.*')
        child.sendline(cur_password)
        ret = child.expect(['.*[Nn]ew password:.*', '[Pp]assword change failed.*', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
        if ret > 0:
            print(f"{child.after}")
            # sys.exit(1)
        child.sendline(new_password)
        child.expect(['[Rr]etype [Nn]ew [Pp]assword:.*', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
        child.sendline(new_password)
        ret = child.expect(['.*[Pp]assword change failed.*', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
        if ret == 0:
            print(f"{child.after}")
            # sys.exit(1)
        if ret > 0:
            response = {"status": False, "message": "Password not changed due to unexpected EOF or timeout"}
            # sys.exit(1)
        child.sendline(new_password)
        ret = child.expect(['all authentication tokens updated successfully', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
        if ret == 0:
            response = {"status": True, "message": "Password Update Successfully."}
            # sys.stdout.flush()
            # sys.exit(0)
        print("Password not changed due to unexpected EOF or timeout")

        # sys.stdout.flush()
        child.interact()
        return response