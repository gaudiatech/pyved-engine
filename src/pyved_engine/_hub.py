"""
PATTERN: dependency injection
------------

Keep this file separate from __init__.py!
its important, bc all sub-modules in kengi may import _hub
in order to refer to other dependencies/sub-modules

"""
import importlib.util


# TODO if this line missing, cant use Add-ons like .gui or .tmx
from .core import events
# TODO need to include the API in the hub, not pygame /!\
# import pygame


class _PyModulePromise:
    verbose = 1
    JIT_MSG_LOADING = '*Pyv add-on "{}" is ready! Loading on-the-fly ok*'

    def __init__(self, mod_name: str, pypath: str, pck_arg: str):
        self._ref_module = None
        self._module_name = mod_name
        self._py_path = pypath
        self.pck_arg = pck_arg

    def is_ready(self):
        return self._ref_module is not None

    @property
    def name(self):
        return self._module_name

    @property
    def result(self):
        if not self.is_ready():
            self._jit_load_module_op(self.pck_arg)
        return self._ref_module

    def _jit_load_module_op(self, pck_arg):
        cls = self.__class__
        if cls.verbose:  # and nam != 'pygame':  # print a debug info.
            print(cls.JIT_MSG_LOADING.format(self.name))
        if (pck_arg is not None) and self._py_path[0] == '.':
            self._ref_module = importlib.import_module(self._py_path, pck_arg)
        else:
            self._ref_module = importlib.import_module(self._py_path)


class Injector:
    """
    gere chargement composants engine + any engine plugin
    Le fait au moyen dun tableau:
    module name <-> instance of LazyModule
    """

    def __init__(self, module_listing, package_arg):
        self._listing = dict()
        for mname, pypath in module_listing.items():
            obj = _PyModulePromise(mname, pypath, package_arg)
            self._listing[obj.name] = obj
        self._man_set = dict()
        self._loading_done = False

    def hack_package_arg(self, new_val):  # useful for the katasdk
        for prom_obj in self._listing.values():
            prom_obj.pck_arg = new_val

    def __contains__(self, item):
        if item in self._man_set:
            return True
        else:
            return item in self._listing

    def set(self, mname, pymod):
        self._man_set[mname] = pymod

    def __getitem__(self, item):
        if item in self._man_set:
            return self._man_set[item]
        else:
            res = self._listing[item].result
            self._loading_done = True
            return res

    def is_loaded(self, pckname):
        return self._listing[pckname].is_ready()

    def register(self, sm_name, py_path, pck_arg):
        if self._loading_done:
            print('***warning*** register plugin should be done before using loading elements')
        self._listing[sm_name] = _PyModulePromise(sm_name, py_path, pck_arg)


kengi_inj = Injector({
    # 'ai': '.looparts.ai',
    # 'demolib': '.looparts.demolib',
    'gui': '.add_ons.gui',
    # 'isometric': '.looparts.isometric',
    # 'polarbear': '.looparts.polarbear',
    'tmx': '.add_ons.tmx',
    # 'anim': '.looparts.anim',
    # 'ascii': '.looparts.ascii',
    'console': '.looparts.console',
    'rogue': '.looparts.rogue',
    # 'rpg': '.looparts.rpg',
    # 'sysconsole': '.looparts.sysconsole',
    'tabletop': '.add_ons.tabletop',
    'terrain': '.looparts.terrain',
}, 'pyved_engine')


def get_injector():
    global kengi_inj
    return kengi_inj


def __getattr__(targ_sm_name):
    if targ_sm_name in kengi_inj:
        return kengi_inj[targ_sm_name]
    else:
        raise AttributeError(f"PYV cannot find any attr./ submodule named {targ_sm_name}")
