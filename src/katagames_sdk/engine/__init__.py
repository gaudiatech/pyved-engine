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
from . import _Injector as InjDedicatedF
from ._BaseGameState import BaseGameState
from ._Injector import Injector
from ._util import underscore_format, camel_case_format


vernum = '22-fire'  # format: « yy-4letterWord » first letter is like the month of build [f]ire - [f]ebruary etc.
injector_obj = Injector()


def plugin_bind(extname, pypath):
    injector_obj.alert_if_needed()
    type(injector_obj).register_plugin(extname, pypath)


def bulk_plugin_bind_op(assoc_extname_pypath):
    injector_obj.alert_if_needed()
    cls = type(injector_obj)
    for ename, pypath in assoc_extname_pypath.items():
        cls.register_plugin(ename, pypath)


def __getattr__(targ_sm_name):
    if targ_sm_name in InjDedicatedF.extra_sm:
        return injector_obj.fetch_sm(targ_sm_name)
    raise AttributeError("module '{}' has no attribute '{}'".format(__name__, targ_sm_name))
