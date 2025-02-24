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
        try:
            child = pexpect.spawnu('/usr/bin/passwd')
            child.expect('[Cc]urrent [Pp]assword:.*')
            child.sendline(old_password)
            ret = child.expect(['.*[Nn]ew password:.*', '[Pp]assword change failed.*', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
            if ret > 0: # password change failed, OEF or timeout
                response["message"] = f"{child.after}"
                self.logger.info(f"ERROR :: ret={ret} {response}")
            else: # current password ok
                child.sendline(new_password)
                child.expect(['[Rr]etype [Nn]ew [Pp]assword:.*', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
                child.sendline(new_password)
                ret = child.expect(['[Aa]ll authentication tokens updated successfully', '.*[Pp]assword change failed.*', pexpect.EOF, pexpect.TIMEOUT], timeout=3)
                if ret == 0: # password change success
                    response["status"] = True
                    response["message"] = "Password Update Successfully."
                    self.logger.info(f"SUCCESS :: Password Update Successfully. {child.before} {child.after}")
                else: # password change failed
                    response["message"] = f"{child.after}"
                    self.logger.info(f"ERROR :: ret={ret} {response}")
            child.close()
        except Exception as exp:
            self.logger.info(f"ERROR :: {exp}")
            response["message"] = f"Unexpected error occured: {exp}"
        return response

