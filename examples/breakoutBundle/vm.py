import importlib.util


class _PyModulePromise:
    verbose = 1
    JIT_MSG_LOADING = ' <>lazy/on-the-fly module loading started... {} now ready to use!'

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
        if cls.verbose:
            print(cls.JIT_MSG_LOADING.format(self.name))
        if (pck_arg is not None) and self._py_path[0] == '.':
            self._ref_module = importlib.import_module(self._py_path, pck_arg)
        else:
            self._ref_module = importlib.import_module(self._py_path)


class Injector:
    def __init__(self, package_arg):
        self._package_arg = package_arg

        self._list_reg_modules = dict()
        self._listing = dict()

    def hack_package_arg(self, new_val):  # useful for the katasdk
        for prom_obj in self._listing.values():
            prom_obj.pck_arg = new_val

    def __contains__(self, item):
        if item in self._list_reg_modules:
            return True
        else:
            return item in self._listing

    def set_prelo_module(self, mname, pymod):
        self._list_reg_modules[mname] = pymod

    def set_lazylo_module(self, sm_name, py_path):
        self._listing[sm_name] = _PyModulePromise(sm_name, py_path, self._package_arg)

    def __getitem__(self, item):
        if item in self._list_reg_modules:
            return self._list_reg_modules[item]
        else:
            return self._listing[item].result

    def is_loaded(self, pckname):
        if pckname in self._list_reg_modules:
            return True
        else:
            return self._listing[pckname].is_ready()


def upwardlink(link_to_pimodules):
    globals()['pimodules'] = link_to_pimodules


from pprint import pprint


def gameexec(metadata, gamedef_mod):
    print('hey this is dummy func instead of gameexec')
    print('metadata is___ ', end='')
    pprint(metadata)

    print('and gamedef is:')
    print(gamedef_mod)
    globals()['pimodules']['pyved_engine'].run_game()
