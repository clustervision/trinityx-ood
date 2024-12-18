#!/bin/bash

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

###
# 
# USAGE:
# cat /etc/ood/config/apps/shell/env
#   OOD_SSH_WRAPPER=/trinity/local/ondemand/3.0/osimage/addons/chroot_wrapper.sh
# 
# cat /trinity/local/ondemand/3.0/osimage/addons/chroot_wrapper.sh
# https://vmware-controller1.cluster:8080/pun/sys/shell/ssh/vmware-controller1.cluster/image=compute,path=/trinity/images/compute,kernel_version=5.14.0-427.37.1.el9_4.x86_64
# 
####


for arg in "$@"; do
    if [[ "$arg" =~ image= ]]; then
        OS_IMAGE=$(echo "$arg" | grep -oP 'image=[^,]+' | cut -d= -f2 | tr -d "'")
    fi
    if [[ "$arg" =~ path= ]]; then
        CHROOT_PATH=$(echo "$arg" | grep -oP 'path=[^,;]+' | cut -d= -f2 | tr -d "'")
    fi
    if [[ "$arg" =~ kernel_version= ]]; then
        FAKE_KERN=$(echo "$arg" | grep -oP 'kernel_version=[^,;]+' | cut -d= -f2 | tr -d "'")
    fi
done

if [[ -n "$OS_IMAGE" && -n "$CHROOT_PATH" && -n "$FAKE_KERN" ]]; then
    if [[ -f /trinity/images/compute/tmp/lchroot.lock ]]; then
        echo "lchroot is already running, waiting for it to finish (press f to force)"

        while [[ -f /trinity/images/compute/tmp/lchroot.lock ]]; do
            read -t 1 -n 1 -s key
            if [[ $key == "f" ]]; then
                echo ""
                echo "Forcing lchroot to stop"
                sudo rm /trinity/images/compute/tmp/lchroot.lock
                break
            else
                echo -n "."
            fi
        done
    fi
    # trap clean EXIT
    # clean() {
    #     sudo rm /trinity/images/compute/tmp/lchroot.lock
    # }
    sudo lchroot $(basename $CHROOT_PATH)
else
    exec /usr/bin/ssh "$@"
fi
