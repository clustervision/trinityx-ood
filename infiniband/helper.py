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
# from log import Log


class Helper():
    """
    All kind of helper methods.
    """

    def __init__(self):
        """
        Constructor - As of now, nothing have to initialize.
        """
        # self.logger = Log.get_logger()
        self.response = {"status": False, "response": None}
        # self.test_response = """
        #     {
        #     "nodes": [
        #         {
        #         "architecture": "",
        #         "burstbuffer_network_address": "",
        #         "boards": 1,
        #         "boot_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cluster_name": "",
        #         "cores": 1,
        #         "specialized_cores": 0,
        #         "cpu_binding": 0,
        #         "cpu_load": 0,
        #         "free_mem": {
        #             "set": false,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cpus": 1,
        #         "effective_cpus": 1,
        #         "specialized_cpus": "",
        #         "energy": {
        #             "average_watts": 0,
        #             "base_consumed_energy": 0,
        #             "consumed_energy": 0,
        #             "current_watts": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #             },
        #             "previous_consumed_energy": 0,
        #             "last_collected": 0
        #         },
        #         "external_sensors": {
        #         },
        #         "extra": "",
        #         "power": {
        #         },
        #         "features": [
        #         ],
        #         "active_features": [
        #         ],
        #         "gpu_spec": "",
        #         "gres": "",
        #         "gres_drained": "N\/A",
        #         "gres_used": "",
        #         "instance_id": "",
        #         "instance_type": "",
        #         "last_busy": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762337277
        #         },
        #         "mcs_label": "",
        #         "specialized_memory": 0,
        #         "name": "jonn-node-ringo",
        #         "next_state_after_reboot": [
        #             "INVALID"
        #         ],
        #         "address": "jonn-node-ringo",
        #         "hostname": "jonn-node-ringo",
        #         "state": [
        #             "DOWN",
        #             "NOT_RESPONDING"
        #         ],
        #         "operating_system": "",
        #         "owner": "",
        #         "partitions": [
        #             "defq",
        #             "compute-group"
        #         ],
        #         "port": 6818,
        #         "real_memory": 100,
        #         "res_cores_per_gpu": 0,
        #         "comment": "",
        #         "reason": "Not responding",
        #         "reason_changed_at": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762337299
        #         },
        #         "reason_set_by_user": "slurm",
        #         "resume_after": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "reservation": "",
        #         "alloc_memory": 0,
        #         "alloc_cpus": 0,
        #         "alloc_idle_cpus": 1,
        #         "tres_used": "",
        #         "tres_weighted": 0.0,
        #         "slurmd_start_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "sockets": 1,
        #         "threads": 1,
        #         "temporary_disk": 0,
        #         "weight": 1,
        #         "tres": "cpu=1,mem=100M,billing=1",
        #         "version": ""
        #         },
        #         {
        #         "architecture": "",
        #         "burstbuffer_network_address": "",
        #         "boards": 1,
        #         "boot_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cluster_name": "",
        #         "cores": 1,
        #         "specialized_cores": 0,
        #         "cpu_binding": 0,
        #         "cpu_load": 0,
        #         "free_mem": {
        #             "set": false,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cpus": 2,
        #         "effective_cpus": 2,
        #         "specialized_cpus": "",
        #         "energy": {
        #             "average_watts": 0,
        #             "base_consumed_energy": 0,
        #             "consumed_energy": 0,
        #             "current_watts": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #             },
        #             "previous_consumed_energy": 0,
        #             "last_collected": 0
        #         },
        #         "external_sensors": {
        #         },
        #         "extra": "",
        #         "power": {
        #         },
        #         "features": [
        #         ],
        #         "active_features": [
        #         ],
        #         "gpu_spec": "",
        #         "gres": "",
        #         "gres_drained": "N\/A",
        #         "gres_used": "",
        #         "instance_id": "",
        #         "instance_type": "",
        #         "last_busy": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762771832
        #         },
        #         "mcs_label": "",
        #         "specialized_memory": 0,
        #         "name": "node001",
        #         "next_state_after_reboot": [
        #             "INVALID"
        #         ],
        #         "address": "node001",
        #         "hostname": "node001",
        #         "state": [
        #             "DOWN",
        #             "DRAIN",
        #             "NOT_RESPONDING"
        #         ],
        #         "operating_system": "",
        #         "owner": "",
        #         "partitions": [
        #             "defq",
        #             "compute-group"
        #         ],
        #         "port": 6818,
        #         "real_memory": 1,
        #         "res_cores_per_gpu": 0,
        #         "comment": "",
        #         "reason": "TRIX-DRAINER: Multiple reasons for drained node, check AlertX for more information",
        #         "reason_changed_at": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762771892
        #         },
        #         "reason_set_by_user": "root",
        #         "resume_after": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "reservation": "",
        #         "alloc_memory": 0,
        #         "alloc_cpus": 0,
        #         "alloc_idle_cpus": 2,
        #         "tres_used": "",
        #         "tres_weighted": 0.0,
        #         "slurmd_start_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "sockets": 2,
        #         "threads": 1,
        #         "temporary_disk": 1,
        #         "weight": 1,
        #         "tres": "cpu=2,mem=1M,billing=2",
        #         "version": ""
        #         },
        #         {
        #         "architecture": "",
        #         "burstbuffer_network_address": "",
        #         "boards": 1,
        #         "boot_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cluster_name": "",
        #         "cores": 1,
        #         "specialized_cores": 0,
        #         "cpu_binding": 0,
        #         "cpu_load": 0,
        #         "free_mem": {
        #             "set": false,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cpus": 1,
        #         "effective_cpus": 1,
        #         "specialized_cpus": "",
        #         "energy": {
        #             "average_watts": 0,
        #             "base_consumed_energy": 0,
        #             "consumed_energy": 0,
        #             "current_watts": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #             },
        #             "previous_consumed_energy": 0,
        #             "last_collected": 0
        #         },
        #         "external_sensors": {
        #         },
        #         "extra": "",
        #         "power": {
        #         },
        #         "features": [
        #         ],
        #         "active_features": [
        #         ],
        #         "gpu_spec": "",
        #         "gres": "",
        #         "gres_drained": "N\/A",
        #         "gres_used": "",
        #         "instance_id": "",
        #         "instance_type": "",
        #         "last_busy": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762771832
        #         },
        #         "mcs_label": "",
        #         "specialized_memory": 0,
        #         "name": "node002",
        #         "next_state_after_reboot": [
        #             "INVALID"
        #         ],
        #         "address": "node002",
        #         "hostname": "node002",
        #         "state": [
        #             "DOWN",
        #             "DRAIN",
        #             "NOT_RESPONDING"
        #         ],
        #         "operating_system": "",
        #         "owner": "",
        #         "partitions": [
        #             "defq",
        #             "compute-group"
        #         ],
        #         "port": 6818,
        #         "real_memory": 100,
        #         "res_cores_per_gpu": 0,
        #         "comment": "",
        #         "reason": "TRIX-DRAINER: Multiple reasons for drained node, check AlertX for more information",
        #         "reason_changed_at": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762771892
        #         },
        #         "reason_set_by_user": "root",
        #         "resume_after": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "reservation": "",
        #         "alloc_memory": 0,
        #         "alloc_cpus": 0,
        #         "alloc_idle_cpus": 1,
        #         "tres_used": "",
        #         "tres_weighted": 0.0,
        #         "slurmd_start_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "sockets": 1,
        #         "threads": 1,
        #         "temporary_disk": 0,
        #         "weight": 1,
        #         "tres": "cpu=1,mem=100M,billing=1",
        #         "version": ""
        #         },
        #         {
        #         "architecture": "x86_64",
        #         "burstbuffer_network_address": "",
        #         "boards": 1,
        #         "boot_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1760631330
        #         },
        #         "cluster_name": "",
        #         "cores": 1,
        #         "specialized_cores": 0,
        #         "cpu_binding": 0,
        #         "cpu_load": 25,
        #         "free_mem": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 10719
        #         },
        #         "cpus": 1,
        #         "effective_cpus": 1,
        #         "specialized_cpus": "",
        #         "energy": {
        #             "average_watts": 0,
        #             "base_consumed_energy": 0,
        #             "consumed_energy": 0,
        #             "current_watts": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #             },
        #             "previous_consumed_energy": 0,
        #             "last_collected": 0
        #         },
        #         "external_sensors": {
        #         },
        #         "extra": "",
        #         "power": {
        #         },
        #         "features": [
        #         ],
        #         "active_features": [
        #         ],
        #         "gpu_spec": "",
        #         "gres": "",
        #         "gres_drained": "N\/A",
        #         "gres_used": "",
        #         "instance_id": "",
        #         "instance_type": "",
        #         "last_busy": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1763378634
        #         },
        #         "mcs_label": "",
        #         "specialized_memory": 0,
        #         "name": "node003",
        #         "next_state_after_reboot": [
        #             "INVALID"
        #         ],
        #         "address": "node003",
        #         "hostname": "node003",
        #         "state": [
        #             "IDLE"
        #         ],
        #         "operating_system": "Linux 5.14.0-570.32.1.el9_6.x86_64 #1 SMP PREEMPT_DYNAMIC Fri Aug 8 18:29:23 UTC 2025",
        #         "owner": "",
        #         "partitions": [
        #             "defq",
        #             "compute-group"
        #         ],
        #         "port": 6818,
        #         "real_memory": 100,
        #         "res_cores_per_gpu": 0,
        #         "comment": "",
        #         "reason": "",
        #         "reason_changed_at": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "reason_set_by_user": "",
        #         "resume_after": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "reservation": "",
        #         "alloc_memory": 0,
        #         "alloc_cpus": 0,
        #         "alloc_idle_cpus": 1,
        #         "tres_used": "",
        #         "tres_weighted": 0.0,
        #         "slurmd_start_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1760631542
        #         },
        #         "sockets": 1,
        #         "threads": 1,
        #         "temporary_disk": 0,
        #         "weight": 1,
        #         "tres": "cpu=1,mem=100M,billing=1",
        #         "version": "24.11.5"
        #         },
        #         {
        #         "architecture": "",
        #         "burstbuffer_network_address": "",
        #         "boards": 1,
        #         "boot_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cluster_name": "",
        #         "cores": 1,
        #         "specialized_cores": 0,
        #         "cpu_binding": 0,
        #         "cpu_load": 0,
        #         "free_mem": {
        #             "set": false,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cpus": 1,
        #         "effective_cpus": 1,
        #         "specialized_cpus": "",
        #         "energy": {
        #             "average_watts": 0,
        #             "base_consumed_energy": 0,
        #             "consumed_energy": 0,
        #             "current_watts": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #             },
        #             "previous_consumed_energy": 0,
        #             "last_collected": 0
        #         },
        #         "external_sensors": {
        #         },
        #         "extra": "",
        #         "power": {
        #         },
        #         "features": [
        #         ],
        #         "active_features": [
        #         ],
        #         "gpu_spec": "",
        #         "gres": "",
        #         "gres_drained": "N\/A",
        #         "gres_used": "",
        #         "instance_id": "",
        #         "instance_type": "",
        #         "last_busy": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762771832
        #         },
        #         "mcs_label": "",
        #         "specialized_memory": 0,
        #         "name": "node004",
        #         "next_state_after_reboot": [
        #             "INVALID"
        #         ],
        #         "address": "node004",
        #         "hostname": "node004",
        #         "state": [
        #             "DOWN",
        #             "DRAIN",
        #             "NOT_RESPONDING"
        #         ],
        #         "operating_system": "",
        #         "owner": "",
        #         "partitions": [
        #             "defq",
        #             "ubuntu-group"
        #         ],
        #         "port": 6818,
        #         "real_memory": 100,
        #         "res_cores_per_gpu": 0,
        #         "comment": "",
        #         "reason": "TRIX-DRAINER: Multiple reasons for drained node, check AlertX for more information",
        #         "reason_changed_at": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762771892
        #         },
        #         "reason_set_by_user": "root",
        #         "resume_after": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "reservation": "",
        #         "alloc_memory": 0,
        #         "alloc_cpus": 0,
        #         "alloc_idle_cpus": 1,
        #         "tres_used": "",
        #         "tres_weighted": 0.0,
        #         "slurmd_start_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "sockets": 1,
        #         "threads": 1,
        #         "temporary_disk": 0,
        #         "weight": 1,
        #         "tres": "cpu=1,mem=100M,billing=1",
        #         "version": ""
        #         },
        #         {
        #         "architecture": "x86_64",
        #         "burstbuffer_network_address": "",
        #         "boards": 1,
        #         "boot_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1760631508
        #         },
        #         "cluster_name": "",
        #         "cores": 1,
        #         "specialized_cores": 0,
        #         "cpu_binding": 0,
        #         "cpu_load": 21,
        #         "free_mem": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 9135
        #         },
        #         "cpus": 1,
        #         "effective_cpus": 1,
        #         "specialized_cpus": "",
        #         "energy": {
        #             "average_watts": 0,
        #             "base_consumed_energy": 0,
        #             "consumed_energy": 0,
        #             "current_watts": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #             },
        #             "previous_consumed_energy": 0,
        #             "last_collected": 0
        #         },
        #         "external_sensors": {
        #         },
        #         "extra": "",
        #         "power": {
        #         },
        #         "features": [
        #         ],
        #         "active_features": [
        #         ],
        #         "gpu_spec": "",
        #         "gres": "",
        #         "gres_drained": "N\/A",
        #         "gres_used": "",
        #         "instance_id": "",
        #         "instance_type": "",
        #         "last_busy": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1763378634
        #         },
        #         "mcs_label": "",
        #         "specialized_memory": 0,
        #         "name": "node005",
        #         "next_state_after_reboot": [
        #             "INVALID"
        #         ],
        #         "address": "node005",
        #         "hostname": "node005",
        #         "state": [
        #             "IDLE",
        #             "DRAIN"
        #         ],
        #         "operating_system": "Linux 5.14.0-570.32.1.el9_6.x86_64 #1 SMP PREEMPT_DYNAMIC Fri Aug 8 18:29:23 UTC 2025",
        #         "owner": "",
        #         "partitions": [
        #             "defq",
        #             "compute-group"
        #         ],
        #         "port": 6818,
        #         "real_memory": 100,
        #         "res_cores_per_gpu": 0,
        #         "comment": "",
        #         "reason": "",
        #         "reason_changed_at": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "reason_set_by_user": "",
        #         "resume_after": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "reservation": "",
        #         "alloc_memory": 0,
        #         "alloc_cpus": 0,
        #         "alloc_idle_cpus": 1,
        #         "tres_used": "",
        #         "tres_weighted": 0.0,
        #         "slurmd_start_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1760631785
        #         },
        #         "sockets": 1,
        #         "threads": 1,
        #         "temporary_disk": 0,
        #         "weight": 1,
        #         "tres": "cpu=1,mem=100M,billing=1",
        #         "version": "24.11.5"
        #         },
        #         {
        #         "architecture": "",
        #         "burstbuffer_network_address": "",
        #         "boards": 1,
        #         "boot_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cluster_name": "",
        #         "cores": 1,
        #         "specialized_cores": 0,
        #         "cpu_binding": 0,
        #         "cpu_load": 0,
        #         "free_mem": {
        #             "set": false,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cpus": 1,
        #         "effective_cpus": 1,
        #         "specialized_cpus": "",
        #         "energy": {
        #             "average_watts": 0,
        #             "base_consumed_energy": 0,
        #             "consumed_energy": 0,
        #             "current_watts": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #             },
        #             "previous_consumed_energy": 0,
        #             "last_collected": 0
        #         },
        #         "external_sensors": {
        #         },
        #         "extra": "",
        #         "power": {
        #         },
        #         "features": [
        #         ],
        #         "active_features": [
        #         ],
        #         "gpu_spec": "",
        #         "gres": "",
        #         "gres_drained": "N\/A",
        #         "gres_used": "",
        #         "instance_id": "",
        #         "instance_type": "",
        #         "last_busy": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762771832
        #         },
        #         "mcs_label": "",
        #         "specialized_memory": 0,
        #         "name": "node006",
        #         "next_state_after_reboot": [
        #             "INVALID"
        #         ],
        #         "address": "node006",
        #         "hostname": "node006",
        #         "state": [
        #             "DOWN",
        #             "DRAIN",
        #             "NOT_RESPONDING"
        #         ],
        #         "operating_system": "",
        #         "owner": "",
        #         "partitions": [
        #             "defq",
        #             "ubuntu-group"
        #         ],
        #         "port": 6818,
        #         "real_memory": 100,
        #         "res_cores_per_gpu": 0,
        #         "comment": "",
        #         "reason": "TRIX-DRAINER: Multiple reasons for drained node, check AlertX for more information",
        #         "reason_changed_at": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762771892
        #         },
        #         "reason_set_by_user": "root",
        #         "resume_after": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "reservation": "",
        #         "alloc_memory": 0,
        #         "alloc_cpus": 0,
        #         "alloc_idle_cpus": 1,
        #         "tres_used": "",
        #         "tres_weighted": 0.0,
        #         "slurmd_start_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "sockets": 1,
        #         "threads": 1,
        #         "temporary_disk": 0,
        #         "weight": 1,
        #         "tres": "cpu=1,mem=100M,billing=1",
        #         "version": ""
        #         },
        #         {
        #         "architecture": "",
        #         "burstbuffer_network_address": "",
        #         "boards": 1,
        #         "boot_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cluster_name": "",
        #         "cores": 1,
        #         "specialized_cores": 0,
        #         "cpu_binding": 0,
        #         "cpu_load": 0,
        #         "free_mem": {
        #             "set": false,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cpus": 1,
        #         "effective_cpus": 1,
        #         "specialized_cpus": "",
        #         "energy": {
        #             "average_watts": 0,
        #             "base_consumed_energy": 0,
        #             "consumed_energy": 0,
        #             "current_watts": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #             },
        #             "previous_consumed_energy": 0,
        #             "last_collected": 0
        #         },
        #         "external_sensors": {
        #         },
        #         "extra": "",
        #         "power": {
        #         },
        #         "features": [
        #         ],
        #         "active_features": [
        #         ],
        #         "gpu_spec": "",
        #         "gres": "",
        #         "gres_drained": "N\/A",
        #         "gres_used": "",
        #         "instance_id": "",
        #         "instance_type": "",
        #         "last_busy": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762337277
        #         },
        #         "mcs_label": "",
        #         "specialized_memory": 0,
        #         "name": "node009",
        #         "next_state_after_reboot": [
        #             "INVALID"
        #         ],
        #         "address": "node009",
        #         "hostname": "node009",
        #         "state": [
        #             "DOWN",
        #             "NOT_RESPONDING"
        #         ],
        #         "operating_system": "",
        #         "owner": "",
        #         "partitions": [
        #             "defq",
        #             "compute-group"
        #         ],
        #         "port": 6818,
        #         "real_memory": 100,
        #         "res_cores_per_gpu": 0,
        #         "comment": "",
        #         "reason": "Not responding",
        #         "reason_changed_at": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762337299
        #         },
        #         "reason_set_by_user": "slurm",
        #         "resume_after": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "reservation": "",
        #         "alloc_memory": 0,
        #         "alloc_cpus": 0,
        #         "alloc_idle_cpus": 1,
        #         "tres_used": "",
        #         "tres_weighted": 0.0,
        #         "slurmd_start_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "sockets": 1,
        #         "threads": 1,
        #         "temporary_disk": 0,
        #         "weight": 1,
        #         "tres": "cpu=1,mem=100M,billing=1",
        #         "version": ""
        #         },
        #         {
        #         "architecture": "",
        #         "burstbuffer_network_address": "",
        #         "boards": 1,
        #         "boot_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cluster_name": "",
        #         "cores": 1,
        #         "specialized_cores": 0,
        #         "cpu_binding": 0,
        #         "cpu_load": 0,
        #         "free_mem": {
        #             "set": false,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cpus": 1,
        #         "effective_cpus": 1,
        #         "specialized_cpus": "",
        #         "energy": {
        #             "average_watts": 0,
        #             "base_consumed_energy": 0,
        #             "consumed_energy": 0,
        #             "current_watts": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #             },
        #             "previous_consumed_energy": 0,
        #             "last_collected": 0
        #         },
        #         "external_sensors": {
        #         },
        #         "extra": "",
        #         "power": {
        #         },
        #         "features": [
        #         ],
        #         "active_features": [
        #         ],
        #         "gpu_spec": "",
        #         "gres": "",
        #         "gres_drained": "N\/A",
        #         "gres_used": "",
        #         "instance_id": "",
        #         "instance_type": "",
        #         "last_busy": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762337277
        #         },
        #         "mcs_label": "",
        #         "specialized_memory": 0,
        #         "name": "node010-wont-show",
        #         "next_state_after_reboot": [
        #             "INVALID"
        #         ],
        #         "address": "node010-wont-show",
        #         "hostname": "node010-wont-show",
        #         "state": [
        #             "DOWN",
        #             "NOT_RESPONDING"
        #         ],
        #         "operating_system": "",
        #         "owner": "",
        #         "partitions": [
        #             "defq",
        #             "compute-group"
        #         ],
        #         "port": 6818,
        #         "real_memory": 100,
        #         "res_cores_per_gpu": 0,
        #         "comment": "",
        #         "reason": "Not responding",
        #         "reason_changed_at": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762337299
        #         },
        #         "reason_set_by_user": "slurm",
        #         "resume_after": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "reservation": "",
        #         "alloc_memory": 0,
        #         "alloc_cpus": 0,
        #         "alloc_idle_cpus": 1,
        #         "tres_used": "",
        #         "tres_weighted": 0.0,
        #         "slurmd_start_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "sockets": 1,
        #         "threads": 1,
        #         "temporary_disk": 0,
        #         "weight": 1,
        #         "tres": "cpu=1,mem=100M,billing=1",
        #         "version": ""
        #         },
        #         {
        #         "architecture": "",
        #         "burstbuffer_network_address": "",
        #         "boards": 1,
        #         "boot_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cluster_name": "",
        #         "cores": 1,
        #         "specialized_cores": 0,
        #         "cpu_binding": 0,
        #         "cpu_load": 0,
        #         "free_mem": {
        #             "set": false,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "cpus": 1,
        #         "effective_cpus": 1,
        #         "specialized_cpus": "",
        #         "energy": {
        #             "average_watts": 0,
        #             "base_consumed_energy": 0,
        #             "consumed_energy": 0,
        #             "current_watts": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #             },
        #             "previous_consumed_energy": 0,
        #             "last_collected": 0
        #         },
        #         "external_sensors": {
        #         },
        #         "extra": "",
        #         "power": {
        #         },
        #         "features": [
        #         ],
        #         "active_features": [
        #         ],
        #         "gpu_spec": "",
        #         "gres": "",
        #         "gres_drained": "N\/A",
        #         "gres_used": "",
        #         "instance_id": "",
        #         "instance_type": "",
        #         "last_busy": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762337277
        #         },
        #         "mcs_label": "",
        #         "specialized_memory": 0,
        #         "name": "renamed-node007",
        #         "next_state_after_reboot": [
        #             "INVALID"
        #         ],
        #         "address": "renamed-node007",
        #         "hostname": "renamed-node007",
        #         "state": [
        #             "DOWN",
        #             "NOT_RESPONDING"
        #         ],
        #         "operating_system": "",
        #         "owner": "",
        #         "partitions": [
        #             "defq",
        #             "compute-group"
        #         ],
        #         "port": 6818,
        #         "real_memory": 100,
        #         "res_cores_per_gpu": 0,
        #         "comment": "",
        #         "reason": "Not responding",
        #         "reason_changed_at": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 1762337299
        #         },
        #         "reason_set_by_user": "slurm",
        #         "resume_after": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "reservation": "",
        #         "alloc_memory": 0,
        #         "alloc_cpus": 0,
        #         "alloc_idle_cpus": 1,
        #         "tres_used": "",
        #         "tres_weighted": 0.0,
        #         "slurmd_start_time": {
        #             "set": true,
        #             "infinite": false,
        #             "number": 0
        #         },
        #         "sockets": 1,
        #         "threads": 1,
        #         "temporary_disk": 0,
        #         "weight": 1,
        #         "tres": "cpu=1,mem=100M,billing=1",
        #         "version": ""
        #         }
        #     ],
        #     "last_update": {
        #         "set": true,
        #         "infinite": false,
        #         "number": 1763385300
        #     },
        #     "meta": {
        #         "plugin": {
        #         "type": "",
        #         "name": "",
        #         "data_parser": "data_parser\/v0.0.42",
        #         "accounting_storage": "accounting_storage\/slurmdbd"
        #         },
        #         "client": {
        #         "source": "\/dev\/pts\/1",
        #         "user": "root",
        #         "group": "root"
        #         },
        #         "command": [
        #         "show"
        #         ],
        #         "slurm": {
        #         "version": {
        #             "major": "24",
        #             "micro": "5",
        #             "minor": "11"
        #         },
        #         "release": "24.11.5",
        #         "cluster": "cluster"
        #         }
        #     },
        #     "errors": [
        #     ],
        #     "warnings": [
        #     ]
        #     }
        #     """
        # self.test_response = json.loads(self.test_response)


    def shell_execute(self, command: str) -> dict:
        """
        This method will execute a command on shell and return the output.
        """
        version_check = subprocess.run([SLURM_VERSION], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, check=False)
        if version_check.returncode == 0:
            slurm_version = version_check.stdout.replace("slurm ", "").strip()
            slurm_version = version.parse(slurm_version)
            if slurm_version >= version.parse("23.11.0"):
                #TODO only for testing
                remote_host = "root@192.168.164.156"
                command = f"ssh {remote_host} '{command}'"
                #TODO only for testing
                execute = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, check=False)
                # print(execute.returncode)
                # print(execute.stdout)
                # print(execute.stderr)
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
        # print("=============")
        # print(slurm_nodes)
        # print("=============")
        if slurm_nodes["status"] is True:
            nodes = slurm_nodes["response"]["nodes"]
            if len(nodes) > 0:# TODO: for testing
            # if self.test_response: # TODO: for testing
                # nodes = self.test_response["nodes"] # TODO: for testing
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
        print("=============")
        print(self.response)
        print("=============")
        return self.response


    def slurm_resume(self, node_list: str) -> dict:
        """
        This method will Resume the Slurm Nodes.
        """
        slurm_resume_cmd = SLURM_RESUME.format(node_list)
        self.response = self.shell_execute(slurm_resume_cmd)
        print("=============")
        print(self.response)
        print("=============")
        return self.response


# if __name__ == "__main__":

#     # slurm_nodes = Helper().slurm_info()
#     # print("=============")
#     # print(slurm_nodes)
#     # print("=============")
#     # node_list = "node[001-005],node007,node[009-010]"
#     node_list = "node[001-005]"
#     slurm_nodes = Helper().slurm_drain(node_list)
#     slurm_nodes = Helper().slurm_resume(node_list)
#     # print("=============")
#     # print(slurm_nodes)
#     # print("=============")