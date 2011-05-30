#!/bin/env python
import os

hacks = """# command-not-found tomfoolery
if [ -e /boot/common/bin/python ]; then
    command_not_found_handle(){
        /boot/common/bin/python /boot/common/bin/command_not_found.py "$1"
    }
else
    command_not_found_handle(){
        echo "$1 not found: try installoptionalpkg $1; and check installoptionalpkg -l"
    }     
fi
"""


default_options="""{
"autocorrect": false, 
"spellcheck": false,
"haikuports": false
}"""
home = os.environ['HOME']
if not os.path.exists("%s/config/settings/command-not-found/options.json" % home):
    profile = open("/etc/profile", "a")
    profile.write(hacks)
    profile.close()
    os.mkdir("%s/config/settings/command-not-found/" % home)
    options = open("%s/config/settings/command-not-found/options.json" % home, "w")
    options.write(default_options)
    options.close()
os.system("cp haiku_cnf.py /boot/common/bin/command_not_found.py")