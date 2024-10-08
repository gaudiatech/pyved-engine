"""
Authors: contact@kata.games *DO NOT EDIT THAT FILE*
(unless you really know what you're doing) Remark: the current file is automatically
generated by PYV /pyved-engine. It's part of the game engine global layout)
To know more, please visit: https://gaudiatech.github.io/pyved-engine/
The following code is standardized, rarely changes, and it helps in booting up
the wrapped/the internal game cartridge (=PyvGAMCART format)
"""
import importlib.util
import os
class _PyModulePromise:
    JIT_MSG_LOADING = ' lazy-loading module:{}... Ready.'
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
        print(f"LVL0 injector:importing[{item}]")
        print(self.registered_modules)
        print()
        if item in self.registered_modules:
            return self.registered_modules[item]
        return self.lazy_loading[item].result
    def is_loaded(self, package_name):
        return package_name in self.registered_modules or self.lazy_loading[package_name].is_ready()
#def upward_link(link_to_pimodules):
#    globals()['pimodules'] = link_to_pimodules
def find_spc_folder(givenfolder, start_path):
    for root, dirs, files in os.walk(start_path):
        if givenfolder in dirs:
            return True
    return False
def game_execution(metadata, game_definition_module):
    global pyved_engine_alias
    # pyv = globals()['pimodules']['pyved_engine']
    pyv = getattr(globals()['glvars'], pyved_engine_alias)

    if pyv.vars.beginfunc_ref is None:
        if hasattr(game_definition_module, 'game'):
            game = getattr(game_definition_module, 'game')
            pyv.vars.beginfunc_ref, \
                pyv.vars.updatefunc_ref, \
                pyv.vars.endfunc_ref = game.enter, game.update, game.exit
    current_folder = os.getcwd()
    if find_spc_folder(metadata['slug'], current_folder):
        adhoc_folder = os.path.join('.', metadata['slug'], 'cartridge')
    elif find_spc_folder('cartridge', current_folder):
        adhoc_folder = os.path.join('.', 'cartridge')
    else:
        raise FileNotFoundError("ERR: Asset dir for pre-loading assets cannot be found!")
    pyv.preload_assets(
        metadata,
        prefix_asset_folder=adhoc_folder+os.sep+metadata['asset_base_folder']+os.sep,
        prefix_sound_folder=adhoc_folder+os.sep+metadata['sound_base_folder']+os.sep,
    )
    pyv.run_game()

# def prep_libs(inj_obj, rel_import_flag, plugins_list):
def prep_libs(cb_func, rel_import_flag, plugins_list):
    # The solution implemented here is WITHOUT INJECTOR obj,
    # we've set directly attributes on the glvars module (such as glvars.pyv ; glvars.netw ; and so on)
    global pyved_engine_alias
    for alias, plugin_name in plugins_list:
        if plugin_name == 'pyved_engine':
            import pyved_engine
            plugin_module = pyved_engine
            pyved_engine_alias = alias

        elif rel_import_flag:
            # Adjusted: Using absolute import with __package__
            module_name = f".lib.{plugin_name}"
            plugin_module = importlib.import_module(module_name, __package__)

        else:
            module_name = f"lib.{plugin_name}"
            plugin_module = importlib.import_module(module_name)

        # Dynamically load the module using importlib.import_module
        print('--setting--')
        print(alias, plugin_module)
        #inj_obj.set_preloaded_module(alias, plugin_module)
        cb_func(alias, plugin_name, plugin_module)

    # inj_obj.set_lazy_loaded_module('pyved_engine', 'pyved_engine')

# -------------------------

# def prep_esper(inj_obj, rel_import_flag):
    # if rel_import_flag:
        # from .plugins import esper33 as esper
    # else:
        # from plugins import esper33 as esper
    # inj_obj.set_lazy_loaded_module('pyved_engine', 'pyved_engine')
    # inj_obj.set_preloaded_module('esper', esper)
# def bootgame(metadata):
    # try:
        # from cartridge import pimodules
        # rel_imports = False
    # except ModuleNotFoundError:
        # from .cartridge import pimodules
        # rel_imports = True
    # mon_inj = Injector(None)
    # mon_inj.set_lazy_loaded_module('pyved_engine', 'pyved_engine')
    # prep_esper(mon_inj, rel_imports)
    # upward_link(mon_inj)
    # if rel_imports:
        # pimodules.upward_link = mon_inj
        # from .cartridge import gamedef
        # game_execution(metadata, gamedef)
    # else:
        # pimodules.upward_link = mon_inj
        # from cartridge import gamedef
        # game_execution(metadata, gamedef)

glvars = None
pyved_engine_alias = None

def bootgame(metadata):
    global glvars
    try:
        from cartridge import glvars as c_glvars
        rel_imports = False
    except ModuleNotFoundError:
        from .cartridge import glvars as c_glvars
        rel_imports = True

    # mon_inj = Injector(None)
    # mon_inj.set_lazy_loaded_module('pyved_engine', 'pyved_engine')

    # read lib list from the metadat
    lib_list = []
    for lib_id in metadata['dependencies'].keys():
        if len(metadata['dependencies'][lib_id])>1:
            alias = metadata['dependencies'][lib_id][1]
            lib_list.append((alias, lib_id))
        else:
            lib_list.append((lib_id, lib_id))
    print('loading libs:',lib_list)

    # bind libs to gl_vars.*
    prep_libs(c_glvars.register_lib, rel_imports, lib_list)
    # fix manually the network lib, like THE LIB expect it to be ...
    if c_glvars.has_registered('network'):
        getattr(c_glvars, c_glvars.get_alias('network')).slugname = metadata['slug']

    # make it available elsewhere
    glvars = c_glvars
    if rel_imports:
        # pimodules.upward_link = mon_inj
        from .cartridge import gamedef
        game_execution(metadata, gamedef)
    else:
        # pimodules.upward_link = mon_inj
        from cartridge import gamedef
        game_execution(metadata, gamedef)

if __name__ == '__main__':  # Keep this if u wish to allow direct script direct execution/No pyv-cli
    import json
    with open('cartridge/metadat.json', 'r') as fp:
        bootgame(json.load(fp))
