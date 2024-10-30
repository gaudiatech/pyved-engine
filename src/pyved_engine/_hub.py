"""
PATTERN: dependency injection
------------

Keep this file separate from __init__.py!
its important, bc all sub-modules in kengi may import _hub
in order to refer to other dependencies/sub-modules

"""
import importlib.util


bundle_name = None
# not the best code layout, but if this line missing
# several add_ons like .tmx or .isometric will break
from .core import events


class PyModulePromise:
    verbose = 1
    JIT_MSG_LOADING = '*Pyv add-on "{}" is ready! Loading on-the-fly ok*'
    ref_to_pygame = None

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

        # Check if the path starts with 'pygame' and strip it for modular navigation
        string = self._py_path
        if string.split('.')[0] == 'pygame':
            # Split the path and discard the 'pygame' part, keeping only the rest
            path_parts = string.split('.')[1:]
            # Start with the base pygame reference
            ref = self.__class__.ref_to_pygame
            # Iterate through each part to navigate to the target attribute
            for part in path_parts:
                print(' getattr called with args::', ref, part)
                ref = getattr(ref, part)
            self._ref_module = ref
            return
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
            obj = PyModulePromise(mname, pypath, package_arg)
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
        if mname == 'pygame':
            PyModulePromise.ref_to_pygame = pymod  # auto- bind
            print('auto bind')
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
        self._listing[sm_name] = PyModulePromise(sm_name, py_path, pck_arg)


_kengi_inj = Injector({
    # lazy-loading due to the pygame emu mechanism...
    'Vector2d': 'pygame.math.Vector2',

    # lazy-loading that may solve performance issues
    # (dont load large modules unless it is necessary):

    # 'ai': '.looparts.ai',
    # 'demolib': '.looparts.demolib',
    'gui': '.add_ons.gui',

    'isometric': '.looparts.isometric',  # required to play demo 'isometric0'
    'polarbear': '.looparts.polarbear',  # used to play demo 'isometric1'
    'tmx': '.add_ons.tmx',
    # 'anim': '.looparts.anim',
    # 'ascii': '.looparts.ascii',
    'console': '.looparts.console',
    'rogue': '.looparts.rogue',
    'rpg': '.looparts.rpg',
    # 'sysconsole': '.looparts.sysconsole',
    'tabletop': '.looparts.tabletop',
    'terrain': '.looparts.terrain',
}, 'pyved_engine')


def __getattr__(targ_sm_name):
    if targ_sm_name in _kengi_inj:
        return _kengi_inj[targ_sm_name]
    else:
        raise AttributeError(f"PYV cannot find any attr./ submodule named {targ_sm_name}")


def get_injector():
    global _kengi_inj
    return _kengi_inj
