import importlib.util


extra_sm = {
    'anim': '._sm_shelf.anim',
    'core': '._sm_shelf.core',
    'event': '._sm_shelf.event',
    'gui': '._sm_shelf.gui',
    'legacy': '._sm_shelf.legacy',
    'network': '._sm_shelf.network',
    'struct': '._sm_shelf.struct',
    'isometric': '._sm_shelf.isometric',
    'tmx': '._sm_shelf.tmx',
    'console': '._sm_shelf.console',

    'pygame': 'pygame',  # hackable by the sdk
}


class Injector:
    """
    gere chargement composants engine + any engine plugin
    """

    package_arg = 'katagames_engine'  # hackable by the sdk

    def __init__(self):
        self._pre_load_st = True
        self.sm_cache = dict()

    def alert_if_needed(self):
        if not self._pre_load_st:
            print('***warning*** register plugin should be done before using any kataen.* element')

    @staticmethod
    def register_plugin(sm_name, py_path):
        global extra_sm
        extra_sm[sm_name] = py_path

    def register_ld_submodule(self, sm_name):
        self.sm_cache[sm_name] = self._lazy_import(sm_name)

    def _lazy_import(self, name):
        global package_arg
        print(f' kengi loads [{name}]')
        self._pre_load_st = False
        pypath = extra_sm[name]
        if pypath[0] == '.':  # relative import detected
            parg = self.__class__.package_arg
            return importlib.import_module(pypath, parg)
        else:
            return importlib.import_module(pypath)


inj_obj = Injector()


def __getattr__(targ_sm_name):
    if targ_sm_name not in inj_obj.sm_cache:
        if targ_sm_name not in extra_sm:
            return None
        inj_obj.register_ld_submodule(targ_sm_name)
    return inj_obj.sm_cache[targ_sm_name]
