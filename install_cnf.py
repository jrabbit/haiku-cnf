#!/bin/env python
import os

hacks = """# command-not-found tomfoolery
if [ -e /boot/common/bin/python]; then
    command_not_found_handle(){
        /boot/common/bin/python /boot/common/bin/command_not_found.py "$1"
    }
else
    command_not_found_handle(){
        echo "$1 not found: try installoptionalpkg $1; and check installoptionalpkg -l"
    }     
fi"""

os.system("echo %s >> /etc/profile" % hacks)
os.system("cp haiku_cnf.py /boot/common/bin/command_not_found.py")