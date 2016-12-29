#!/bin/env python
import os

hacks = """# command-not-found tomfoolery
if [ -e /system/bin/python ]; then
    command_not_found_handle(){
        /boot/system/bin/python /boot/system/non-packaged/bin/command_not_found.py "$1"
    }
else
    command_not_found_handle(){
        echo "$1 not found: try pkgman install $1; and check pkgman search $1"
    }     
fi
\n
"""


default_options="""{
"autocorrect": false, 
"spellcheck": false,
"haikuports": false
}\n"""

def main():
    home = os.environ['HOME']
    if not os.path.exists("%s/config/settings/command-not-found/options.json" % home):
        profile = open("/etc/profile", "a")
        profile.write(hacks)
        profile.close()
        os.mkdir("%s/config/settings/command-not-found/" % home)
        options = open("%s/config/settings/command-not-found/options.json" % home, "w")
        options.write(default_options)
        options.close()
    os.system("install -m 755 haiku_cnf.py /boot/system/non-packaged/bin/command_not_found.py")


if __name__ == '__main__':
    main()
