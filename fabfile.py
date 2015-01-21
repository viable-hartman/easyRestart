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
# Import socket for IP lookups
import socket
# Globally disable SSL Certificat verification
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


# Globals.  These could also be Fabric-Bolt parameters
# env.key_filename = '/opt/fabric/.ssh/id_rsa'
# env.reject_unknown_hosts = False
# env.disable_known_hosts = True
env.path = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
# env.shell = "/bin/bash -l -c"
# env.use_shell = True
# env.always_use_pty = True

f5man = None

# Global wrapper for F5 control
def bounceF5():
    def closuref(func):
        def innerclosuref(*args, **kwargs):
            global f5man
            try:
                if not(f5man):  # F5 Manager instantiated
                    f5_config = {
                        "server": env.f5ip,
                        "port": int(env.f5port),
                        "user": env.f5user,
                        "passw": env.f5pass
                    }
                    f5man = F5Manager(**f5_config)
                if(f5man):  # F5 Manager instantiated
                    pools = json.loads(env.f5pools)
                    member = {'address': socket.gethostbyname(env.host), 'port': env.memberport}
                    f5man.disableMember(member, pools)
                    func(*args, **kwargs)
                    f5man.enableMember(member, pools)
                else:
                  logging.critical(red('F5 Manager failed to instantiate.'))
            except Exception:
                traceback.print_exc()
        return wraps(func)(innerclosuref)
    return closuref

@task
@bounceF5()
@parallel
def Restart():
    sudo('/sbin/restart %s' % env.service);

@task
@parallel
def test_env(argument="nothing"):
    print("Task Arguments:")
    print argument
    print

    print("Task Env:")
    for x, y in env.iteritems():
        print '{}: {}'.format(x, y)
