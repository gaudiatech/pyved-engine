import importlib.util
from pprint import pprint

class _PyModulePromise:
    verbose = 1
    JIT_MSG_LOADING = ' On-the-fly module loading started... {} now ready to use!'

    def __init__(self, module_name: str, python_path: str, package_arg: str):
        self._ref_module = None
        self._module_name = module_name
        self._py_path = python_path
        self.package_arg = package_arg

    def is_ready(self):
        return self._ref_module is not None

    @property
    def name(self):
        return self._module_name

    @property
    def result(self):
        if not self.is_ready():
            self._jit_load_module_op(self.package_arg)
        return self._ref_module

    def _jit_load_module_op(self, package_arg):
        cls = self.__class__
        if cls.verbose:
            print(cls.JIT_MSG_LOADING.format(self.name))
        if package_arg and self._py_path[0] == '.':
            self._ref_module = importlib.import_module(self._py_path, package_arg)
        else:
            self._ref_module = importlib.import_module(self._py_path)

class Injector:
    def __init__(self, package_arg):
        self.package_arg = package_arg
        self.registered_modules = {}
        self.lazy_loading = {}

    def hack_package_arg(self, new_val):
        for promise_obj in self.lazy_loading.values():
            promise_obj.package_arg = new_val

    def __contains__(self, item):
        return item in self.registered_modules or item in self.lazy_loading

    def set_preloaded_module(self, module_name, python_module):
        self.registered_modules[module_name] = python_module

    def set_lazy_loaded_module(self, sub_module_name, python_path):
        self.lazy_loading[sub_module_name] = _PyModulePromise(sub_module_name, python_path, self.package_arg)

    def __getitem__(self, item):
        return self.registered_modules.get(item, self.lazy_loading[item].result)

    def is_loaded(self, package_name):
        return package_name in self.registered_modules or self.lazy_loading[package_name].is_ready()


def upward_link(link_to_pimodules):
    globals()['pimodules'] = link_to_pimodules


def game_execution(metadata, game_definition_module):
    pprint(metadata)
    # TODO handle special case
    # --- detect a special case here: if @pyv.declare_begin
    # and similar tags havent been used manually,
    # I shall detect the proper game object and link stuff here,
    # before calling run_game...

    globals()['pimodules']['pyved_engine'].run_game()
