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
Helper Class for the Infiniband Application.
"""
__author__      = "Sumit Sharma"
__copyright__   = "Copyright 2025, TrinityX[AlertX]"
__license__     = "GPL"
__version__     = "2.0"
__maintainer__  = "Sumit Sharma"
__email__       = "sumit.sharma@clustervision.com"
__status__      = "Development"


import json
import subprocess
from packaging import version
from constant import SLURM_VERSION, SLURM_INFO, SLURM_DRAIN, SLURM_RESUME
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
        self.response = {"status": False, "response": None}


    def shell_execute(self, command: str) -> dict:
        """
        This method will execute a command on shell and return the output.
        """
        version_check = subprocess.run([SLURM_VERSION], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, check=False)
        if version_check.returncode == 0:
            slurm_version = version_check.stdout.replace("slurm ", "").strip()
            slurm_version = version.parse(slurm_version)
            if slurm_version >= version.parse("23.11.0"):
                ############################################################################## TODO only for testing
                # remote_host = "root@192.168.164.156"
                # command = f"ssh {remote_host} '{command}'"
                ############################################################################## TODO only for testing
                execute = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, check=False)
                if execute.returncode == 0:
                    if len(execute.stdout) > 0:
                        try:
                            data = json.loads(execute.stdout)
                            self.response = {"status": True, "response": data}
                        except json.JSONDecodeError as exp:
                            self.response["response"] = exp
                    else:
                        self.response = {"status": True, "response": "Operation done"}
                else:
                    self.response["response"] = execute.stderr
            else:
                self.response["response"] = f"slurm_version {slurm_version} is below then 23.11.0, Please upgrade the Slurm Version."            
        else:
            self.response["response"] = version_check.stdout
        return self.response


    def slurm_info(self) -> dict:
        """
        This method will provide the Slurm Nodes Information.
        """
        slurm_nodes = self.shell_execute(SLURM_INFO)
        if slurm_nodes["status"] is True:
            nodes = slurm_nodes["response"]["nodes"]
            if len(nodes) > 0:
                response = []
                for node in nodes:
                    states = [s.lower() for s in node["state"]]
                    if any(x in states for x in ["down", "unknown", "not_responding"]):
                        response.append({"name": node["name"], "state": "down"})
                    elif any(x in states for x in ["drain"]):
                        if "IB Analyzer drained node" in node["reason"]:
                            response.append({"name": node["name"], "state": "drain", "reason": "IB Analyzer drained node"})
                        else:
                            response.append({"name": node["name"], "state": "drain", "reason": node["reason"]})
                    elif any(x in states for x in ["idle", "busy", "mixed", "allocated"]):
                        response.append({"name": node["name"], "state": "idle"})
                self.response = {"status": True, "response": response}
            else:
                self.response["response"] = "No Nodes available at this time."
        else:
            self.response["response"] = slurm_nodes["response"]
        return self.response


    def slurm_drain(self, node_list: str) -> dict:
        """
        This method will drain the Slurm Nodes.
        """
        slurm_drain_cmd = SLURM_DRAIN.format(node_list)
        self.response = self.shell_execute(slurm_drain_cmd)
        return self.response


    def slurm_resume(self, node_list: str) -> dict:
        """
        This method will Resume the Slurm Nodes.
        """
        slurm_resume_cmd = SLURM_RESUME.format(node_list)
        self.response = self.shell_execute(slurm_resume_cmd)
        return self.response
