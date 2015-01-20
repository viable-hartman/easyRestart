#!/usr/bin/env python

from __future__ import with_statement
# Import used for Fabric parallel ssh commands
from fabric.api import *
from fabric.exceptions import NetworkError
from fabric.colors import red, green
# Import used for system and OS interactions
import os
import sys
# JSON library for loading json config
import json
# Import used for logging concerns
import logging
# Import used for debugging
import traceback
# Import used for decorator pattern
from functools import wraps
# Import F5 Manager code
sys.path.insert(0, '/opt/RadRockingScripts/F5Scripts')
from f5manager import F5Manager
# Globally disable SSL Certificat verification
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


#Globals.  These could also be Fabric-Bolt parameters
env.key_filename = '/opt/fabric/.ssh/id_rsa'
env.reject_unknown_hosts = False
env.disable_known_hosts = True
env.path = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
# env.shell = "/bin/bash -l -c"
# env.use_shell = True
# env.always_use_pty = True
# env.hosts = ['10.254.222.153', '10.254.222.154']
env.hosts = []
memberport = '8090'
# f5pools = ['solr-sandbox']
f5pools = []

config_file = '/opt/fabric/.f5config'
config = {}
f5man = None
with open("%s" % (config_file), 'r') as inFile:
    config = json.load(inFile)
    try:
        f5_config = config['F5_config']
        f5man = F5Manager(**f5_config)
    except Exception:
        traceback.print_exc()

# Global wrapper for F5 control
def bounceF5(members, port, pools):
    def closuref(func):
        def innerclosuref(*args, **kwargs):
            if(f5man):  # F5 Manager instantiated
                for host in members:
                    member = {'address': host, 'port': port}
                    f5man.disableMember(member, pools)
                    func(*args, **kwargs)
                    f5man.enableMember(member, pools)
            else:
              logging.critical(red('F5 Manager failed to instantiate.'))
        return wraps(func)(innerclosuref)
    return closuref


@bounceF5(env.hosts, memberport, f5pools)
@parallel
def easyRestart():
    sudo('ls -lad /root');