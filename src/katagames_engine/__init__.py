"""
Author: github.com/wkta
Principles: The ultimate engine
-------------------------------
 * is a wrapper around pygame functions & objects

 * runs best within the KataSDK but can also be detached and runs independently.
 Just rename _engine -> engine, and Voila

 * does not know ANYTHING about whether it runs in web ctx or not.
 The engine can be "hacked" so it runs a pygame emulator instead of pygame,
 but this does not change anythin' to engine's implementation per se

 * is extensible: engine needs to be able to receive extensions like a GUI manager,
 an isometric engine, etc. without any architecture change.
 To achieve this we will use the same hacking method as previously,
 basically this is like using an Injector (relates to-> Dependency Injection pattern)
 that is:
 if an extension module is called it will be searched/fetched via the Injector.
 This searching is done via __getattr__(name) and the _available_sub_modules dict. structure

"""
from . import _hub
from ._BaseGameState import BaseGameState
from ._util import underscore_format, camel_case_format
from .foundation import defs
from .__version__ import ENGI_VERSION as vernum


def set_package_arg(parg):
    _hub.Injector.package_arg = parg
    print('new package_arg set:', parg)


def plugin_bind(extname, pypath):
    _hub.instance.alert_if_needed()
    _hub.Injector.register_plugin(extname, pypath)


def bulk_plugin_bind_op(assoc_extname_pypath):
    _hub.instance.alert_if_needed()
    for ename, pypath in assoc_extname_pypath.items():
        _hub.Injector.register_plugin(ename, pypath)


def __getattr__(targ_sm_name):
    if targ_sm_name not in _hub.extra_sm.keys():
        raise KeyError('sub-module "{}" you request from Kengi cannot be found!'.format(targ_sm_name))
    else:
        try:
            return getattr(_hub, targ_sm_name)
        except AttributeError:
            raise AttributeError("(kengi injector) _hub has no valid attribute '{}'".format(targ_sm_name))
