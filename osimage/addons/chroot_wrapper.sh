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
    lock_file="$CHROOT_PATH/tmp/lchroot.lock"
    sudo rm -rf "$lock_file"

cat << MYEOF > /tmp/ood-osimage-chroot-$$.sh
#!/bin/bash
    set -e
    NEED_UMOUNT_DEV=1
    NEED_UMOUNT_SYS=1
    NEED_UMOUNT_PROC=1

    function clean {
        [ -z \$CHROOT_PATH ] && return 0
        [ \$NEED_UMOUNT_DEV -eq 1 ] && umount -f $CHROOT_PATH/dev
        [ \$NEED_UMOUNT_PROC -eq 1 ] && umount -f $CHROOT_PATH/proc
        [ \$NEED_UMOUNT_SYS -eq 1 ] && umount -f $CHROOT_PATH/sys
        rm -f $CHROOT_PATH/tmp/lchroot.lock
    }

    function mount_d {
        mount -t devtmpfs devtmpfs  $CHROOT_PATH/dev  2>/dev/null || NEED_UMOUNT_DEV=0
        mount -t sysfs    sysfs     $CHROOT_PATH/sys  2>/dev/null || NEED_UMOUNT_SYS=0
        mount -t proc     proc      $CHROOT_PATH/proc 2>/dev/null || NEED_UMOUNT_PROC=0
    }

    if [ "x${OS_IMAGE}" = "x" ]; then
        echo "osimage need to be specified."
        echo "Type 'luna osimage list' to get the list."
        exit 7
    fi

    echo "OS IMAGE: $OS_IMAGE"
    echo "IMAGE PATH: $CHROOT_PATH"
    echo "FAKE_KERN: $FAKE_KERN"

    if [ -f $CHROOT_PATH/tmp/lchroot.lock ]; then
        TMP=\$(cat $CHROOT_PATH/tmp/lchroot.lock)
        echo "File $CHROOT_PATH/tmp/lchroot.lock exists."
        echo "Currently \${TMP} is using lchroot. Exiting."
        exit 9
    fi

    CUR_TTY=\$(tty)
    CUR_PID=\$$
    echo "PID \${CUR_PID} on \${CUR_TTY}" > $CHROOT_PATH/tmp/lchroot.lock

    trap clean EXIT
    mount_d

    FAKE_KERN=$FAKE_KERN LD_PRELOAD=libluna-fakeuname.so PS1="chroot [\u@$OS_IMAGE \W]# " chroot "$CHROOT_PATH"
MYEOF

    sudo bash /tmp/ood-osimage-chroot-$$.sh
    rm -f /tmp/ood-osimage-chroot-$$.sh

else
    exec /usr/bin/ssh "$@"
fi
