import importlib.util

package_arg = 'katagames_engine'  # MODIFY this, if not using the engine stand-alone

extra_sm = {
    'anim': '._sm_shelf.anim',
    'core': '._sm_shelf.core',
    'event': '._sm_shelf.event',
    'legacy': '._sm_shelf.legacy',
    'struct': '._sm_shelf.struct',
    'isometric': '._sm_shelf.isometric',
    'tmx': '._sm_shelf.tmx',

    'pygame': 'pygame',
}


class Injector:
    """
    gere chargement composants engine + any engine plugin
    """

    def __init__(self):
        self._pre_load_st = True
        self._sm_cache = dict()

    def alert_if_needed(self):
        if not self._pre_load_st:
            print('***warning*** register plugin should be done before using any kataen.* element')

    @staticmethod
    def register_plugin(sm_name, py_path):
        global extra_sm
        extra_sm[sm_name] = py_path

    def fetch_sm(self, sm_name):
        if sm_name in self._sm_cache:
            return self. _sm_cache[sm_name]
        else:
            t = self._lazy_import(sm_name)
            self._sm_cache[sm_name] = t
            return t

    def _lazy_import(self, name):
        global package_arg
        print('...lazy load {}'.format(name))
        self._pre_load_st = False
        pypath = extra_sm[name]
        if pypath[0] == '.':  # relative import detected
            return importlib.import_module(pypath, package_arg)
        else:
            return importlib.import_module(pypath)


instance = Injector()


def __getattr__(targ_sm_name):
    if targ_sm_name in extra_sm:
        return instance.fetch_sm(targ_sm_name)
