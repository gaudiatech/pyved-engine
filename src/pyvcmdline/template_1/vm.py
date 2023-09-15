import importlib.util
from pprint import pprint
import os


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


def find_spc_folder(givenfolder, start_path):
    for root, dirs, files in os.walk(start_path):
        if givenfolder in dirs:
            return True
    return False


def game_execution(metadata, game_definition_module):
    print(f'~~Vm Pyv~~ LAUNCHING {metadata["game_title"]}...')
    print('-'*8 + 'metadata' + '-'*8)
    pprint(metadata)
    print()

    pyv = globals()['pimodules']['pyved_engine']
    # <> Here we have to handle a special case
    # ->to detect: if @pyv.declare_begin etc were not set.
    # If so, and if gamedef has an object named "game" therefore we link all by ourselves
    if pyv.vars.beginfunc_ref is None:
        if hasattr(game_definition_module, 'game'):
            game = getattr(game_definition_module, 'game')
            # this manually connects existing codebase with the pyved 23.8a1+ philosophy (tags)
            pyv.vars.beginfunc_ref, \
                pyv.vars.updatefunc_ref, \
                pyv.vars.endfunc_ref = game.enter, game.update, game.exit

    # Strat= we preload all assets ->best solution considering the wanted code portability
    # ... And no need to filter out the metadata here, pyv can handle the whole thing
    current_folder = os.getcwd()
    if find_spc_folder(metadata['cartridge'], current_folder):
        adhoc_folder = os.path.join('.', metadata['cartridge'], 'cartridge')
    elif find_spc_folder('cartridge', current_folder):
        adhoc_folder = os.path.join('.', 'cartridge')
    else:
        raise FileNotFoundError("ERR: Asset dir for pre-loading assets cannot be found!")
    pyv.preload_assets(metadata, prefix_asset_folder=adhoc_folder+os.sep)

    # lets rock!
    pyv.run_game()
