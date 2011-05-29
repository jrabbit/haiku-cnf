#!/bin/env python
import os
import sys
import json
import anydbm
from subprocess import Popen, PIPE

def update_db():
    """Update the db for when haikuports gets installed or user selects to
    use spellchecking."""
    db = get_db()
    db['base-pkgs'] = json.dumps(read_basepkgs())
    if Popen(['which', 'haikuports'],stdout=PIPE).communicate()[0]:
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
            cmds = cmds + db[x]
    return cmds

def get_options():
    home = os.path.expanduser('~')
    directory = os.path.join(home,"config", "settings","command-not-found")
    config = os.path.join(directory, "options.json")
    return json.load(config)

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
    haikuports = [x.split('/')[1] for x in Popen(['haikuports', 'list'],stdout=PIPE).communicate()[0]]
    return haikuports

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
    command = sys.argv[1] 
    options = get_options()
    if 'meta-setup' not in get_db():
        firstrun()
    if options['spellcheck']:
        for word in similar(command):
            if word in all_cmds():
                if options['autocorrect'] and cmd_installed(word):
                    os.system(' '.join([word] + sys.argv[2:]))
                else:
                    print "Did you mean %s" % word
    else:
        if command in optional_pkg():
            print "This application is availible via `installoptionalpackage %s`" \
            % command
        elif 'haikuports' in options:
            if command in get_db('haikuports'):
                pass
        else:
            print "%s : Command not found. Sorry." % command
    if sys.argv[1].lower() == 'updatedb':
        update_db()
    elif sys.argv[1].lower() == '--debug':
        print all_cmds(), get_db(), get_options()
    elif len(sys.argv) < 2 or sys.argv[1] is '-h':
        print help()