# Automatically generated, do not edit!
# detached server for the bundle "TheGrid"
# pyved version 25.4a1


import os  # to access env variables
import pyved_engine
from netcode.shared_code import glvars
from netcode import run_server

glvars.pyv = pyved_engine.get_engine_router()
glvars.pyv.server_flag=True

# as long as you dont booststrap you cant use .umediator etc
glvars.pyv.bootstrap_e()

PORTINFO = 12881#os.getenv('PORT')
HOSTINFO = 'localhost'#os.getenv('IP')
print('starting game server,',PORTINFO,';',HOSTINFO)
run_server.exec(**{'port':PORTINFO,'host':HOSTINFO,'mode':'ws'})
