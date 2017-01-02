#!/bin/env python
#GPL v3 (c) 2011, 2016 Jack Laxson "jrabbit"
import anydbm
import json
import os
import pprint
import sys
from subprocess import PIPE, Popen, check_output


def update_db():
    """Update the db for when haikuports gets installed or user selects to
    use spellchecking."""
    db = get_db()
    db['base-pkgs'] = json.dumps(read_basepkgs())
    if Popen(['which', 'haikuporter'],stdout=PIPE).communicate()[0]:
        home = os.path.expanduser('~')
        options = open("%s/config/settings/command-not-found/options.json" % home, "w")
        d = json.load(options)
        d['haikuports'] = True
        json.dump(d, options)
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
    return json.load(open(config, "r"))

def search_provides(cmd):
    out = check_output(['pkgman', 'search', '--details', 'cmd:{}'.format(cmd)])
    split = out.splitlines()
    if out.startswith("No matching packages found."):
        return None
    else:
        rest = out.splitlines()[2:]
        return [{"name": i.split()[1], "repo":i.split()[0]} for i in rest]


def read_installopt():
    iop_pkgs = []
    datadir = Popen(['finddir', 'B_COMMON_DATA_DIRECTORY'],stdout=PIPE).communicate()[0].strip()
    #I'm not going to check OptionalLibPackages because no one will call a 
    #library from the cli.
    filename = os.path.join(datadir, 'optional-packages/OptionalPackages')
    for line in open(filename):
        if len(line.split()) > 3:
            if line.split()[2] == 'IsOptionalHaikuImagePackageAdded':
                iop_pkgs.append(line.split()[3].lower())
    return iop_pkgs  

def read_basepkgs():
    baseapps = []
    for x in os.environ['PATH'].split(':'):
        if x is not ".": #Why the hell is this in $PATH?
            baseapps = baseapps + os.listdir(x)
    return baseapps

def read_haikuports():
    return check_output(["haikuporter", "-l"]).splitlines()

def firstrun():
    "Cache existing packages for later use"
    db = get_db() 
    db['iop-pkgs'] = json.dumps(read_installopt())
    db['base-pkgs'] = json.dumps(read_basepkgs())
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

def help():
    "Return help with refrence to invocation name"
    return """Command Not Found -- Haiku 
    Normal usage as invoked by bash: %(app)s [command]
    To update the database: %(app)s updatedb
    To print this help message: %(app)s -h
    To print debug information: %(app)s --debug
    --
    %(app)s reads options from ~/config/settings/command-not-found/options.json""" % {'app': sys.argv[0]}

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print help()
        sys.exit()
    command = sys.argv[1] 
    options = get_options()
    if 'meta-setup' not in get_db():
        firstrun()
    if sys.argv[1].lower() == 'updatedb':
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
                    os.system(' '.join([word] + sys.argv[2:]))
                else:
                    print "Did you mean %s" % word
    else:
        db = get_db()
        if command in db['iop-pkgs']:
            #works
            print "This application is availible via `installoptionalpackage %s`" \
            % command
        elif options['haikuports'] == True:
            if command in db['haikuports']:
                print "This application is availible via `haikuporter -i %s`" % command
        else:
            print "%s : Command not found. Sorry." % command
