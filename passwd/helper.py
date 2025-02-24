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
Helper Class for the PASSWD Application.
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2025, TrinityX[PASSWD]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Development"


import pexpect
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
        This method will use pexpect and update the user Password.
        """
        response = {"status": False, "message": "Password Update Failed."}
        child = pexpect.spawnu('/usr/bin/passwd')
        child.expect('[Cc]urrent [Pp]assword:.*')
        child.sendline(old_password)
        ret = child.expect(['.*[Nn]ew password:.*', '[Pp]assword change failed.*', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
        if ret > 0:
            response["message"] = f"{child.after}"
            self.logger.info(f"ERROR :: {child.after}")
        else:
            child.sendline(new_password)
            child.expect(['[Rr]etype [Nn]ew [Pp]assword:.*', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
            child.sendline(new_password)
            ret = child.expect(['.*[Pp]assword change failed.*', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
            if ret > 0:
                if "all authentication tokens updated successfully" in str(child.before).strip():
                    response["status"] = True
                    response["message"] = "Password Update Successfully."
                    self.logger.info(f"SUCCESS :: Password Update Successfully. {ret} {child.before} {child.after}")
                else:
                    response["message"] = f"Password not changed due to unexpected EOF or timeout. {child.after}"
                    self.logger.info(f"ERROR :: {child.after}")
            if ret == 0:
                response["message"] = f"{child.after}"
                self.logger.info(f"ERROR :: {child.after}")
        child.interact()
        child.close()
        return response

