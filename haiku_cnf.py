#!/bin/env python
#GPL v3 (c) 2011, 2016-2017 Jack Laxson "jrabbit"
import anydbm
import json
import os
import pprint
import logging
import sys
from subprocess import PIPE, Popen, check_output

logger = logging.getLogger(__name__)

def update_db():
    """Update the db for when haikuports gets installed or user selects to
    use spellchecking."""
    db = get_db()
    db['base-pkgs'] = json.dumps(read_basepkgs())
    if Popen(['which', 'haikuporter'],stdout=PIPE).communicate()[0]:
        home = os.path.expanduser('~')
        with open("%s/config/settings/command-not-found/options.json" % home, "w") as options: 
            d = json.load(options)
            d['haikuports'] = True
            # json.dump(d, options)
            db['haikuports'] = json.dumps(read_haikuports())

def get_db(name="filenames"):
    home = os.path.expanduser('~')
    directory = os.path.join(home,"config", "settings","command-not-found")
    return anydbm.open(os.path.join(directory, name), 'c')

def all_cmds():
    db = get_db()
    cmds = []
    for x in db:
        if x.split('-')[0] not in ['haikuports', 'meta']:
            cmds = cmds + json.loads(db[x])
    return cmds

def get_options():
    home = os.path.expanduser('~')
    directory = os.path.join(home,"config", "settings","command-not-found")
    config = os.path.join(directory, "options.json")
    with open(config, 'r') as f:
        return json.load(f)

def search_provides(cmd):
    out = check_output(['pkgman', 'search', '--details', 'cmd:{}'.format(cmd)])
    split = out.splitlines()
    if out.startswith("No matching packages found."):
        return None
    else:
        rest = out.splitlines()[2:]
        return [{"name": i.split()[1], "repo":i.split()[0]} for i in rest]

def read_pkgman():
    out = check_output(['pkgman', 'search', '-a', '--details'])
    rest = out.splitlines()[2:]
    return [i.split()[1] for i in rest]

def read_basepkgs():
    baseapps = []
    for x in os.environ['PATH'].split(':'):
        if x is not ".": #Why the hell is this in $PATH?
            try:
                baseapps = baseapps + os.listdir(x)
            except OSError:
                # This means the folder doesn't exist but is in $PATH
                pass
    return baseapps

def read_haikuports():
    return check_output(["haikuporter", "-l"]).splitlines()

def firstrun():
    """Cache existing packages for later use"""
    db = get_db() 
    db['base-pkgs'] = json.dumps(read_basepkgs())
    db['haikudepot'] = json.dumps(read_pkgman())
    db['builtins'] = json.dumps(['function', 'set', 'false', 'help', 'mapfile', 'getopts', 'compopt', 'cd', 'return', 'enable', 'export', 'pushd', 'type', 'printf', 'jobs', 'times', 'coproc', 'select', 'if', 'logout', 'job_spec', 'for', 'ulimit', 'popd', 'umask', 'readonly', 'source', 'builtin', 'exit', 'suspend', 'wait', 'local', 'until', 'dirs', 'bg', 'hash', 'complete', 'compgen', 'exec', 'read', 'time', 'break', 'test', 'pwd', 'fc', 'let', 'eval', 'fg', 'disown', 'echo', 'true', 'unalias', 'case', 'typeset', 'bind', 'caller', 'shopt', 'alias', 'while', 'continue', 'command', 'trap', 'shift', 'kill', 'readarray', 'declare', 'unset', 'history'])
    db['meta-setup'] = 'True'

def similar(word):
    """Return a set with spelling1 distance alternative spellings
    based on http://norvig.com/spell-correct.html
    From https://launchpad.net/command-not-found (GPLv2)"""
    
    alphabet = 'abcdefghijklmnopqrstuvwxyz-_0123456789'
    s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in s if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in s for c in alphabet if b]
    inserts    = [a + c + b     for a, b in s for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

def cmd_installed(cmd):
    return True


def our_help():
    """Return help with refrence to invocation name"""
    return """Command Not Found -- Haiku 
    Normal usage as invoked by bash: %(app)s [command]
    To update the database: %(app)s updatedb
    To print this help message: %(app)s -h
    To print debug information: %(app)s --debug
    --
    %(app)s reads options from ~/config/settings/command-not-found/options.json""" % {'app': sys.argv[0]}

def cnf(command):
    logger.debug("Entered CNF: %s", command)
    db = get_db()
    provides_info = search_provides(command)
    if options['haikuports'] == True:
        logger.debug("CNF: Haikuports check")
        if command in json.loads(db['haikuports']):
            print("This application is availible via `haikuporter -i %s`" % command)
    elif command in json.loads(db['haikudepot']):
        print("This application is aviaiblible via pkgman install {}".format(command))
    elif provides_info:
        if len(provides_info) == 1:
            print("This application is aviaiblible via pkgman install {}".format(command))
        else:
            print("I found multiple potential packages for {}".format(command))
            print("Try one of these: {}".format(provides_info))
    else:
        print("{} : Command not found. Sorry.".format(command))

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print(our_help())
        sys.exit()
    logging.basicConfig(level=logging.DEBUG)
    command = sys.argv[1]
    options = get_options()
    if 'meta-setup' not in get_db():
        logger.debug("Running for first time")
        firstrun()
    if sys.argv[1].lower() == 'updatedb':
        logger.debug("Updating database")
        update_db()
        sys.exit()
    elif sys.argv[1].lower() == '--debug':
        pprint.pprint(all_cmds())
        pprint.pprint(get_db())
        pprint.pprint(get_options())
        sys.exit()
    if options['spellcheck']:
        for word in similar(command):
            if word in all_cmds():
                if options['autocorrect'] and cmd_installed(word):
                    # I'm pretty sure this is a bad idea.
                    os.system(' '.join([word] + sys.argv[2:]))
                    # os.system is actually sub-call or something and doesn't take over.
                    # Need to escape the for loop
                    sys.exit()
                else:
                    # So when we get here we should still say CNF right?
                    print("Did you mean %s" % word)
                    cnf(command)
                    # Need to escape the for loop
                    sys.exit()
        # Its possible to get here?
        cnf(command)
    else:
        cnf(command)
