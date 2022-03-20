"""
 PATTERN:
 dependency injection
"""
import importlib.util


class ModuleLazyLoader:

    def __init__(self, mod_name: str, pypath: str):
        self._m = None
        self._name = mod_name
        self._pypath = pypath

    @property
    def ready(self):
        return self._m is not None

    @property
    def pymod(self):  # ensure mod is ready before calling this
        return self._m

    @property
    def name(self):
        return self._name

    def load_now(self, parg):
        nam = self.name
        print(f' lazy loading: {nam}')
        if self._pypath[0] == '.':  # relative import detected
            self._m = importlib.import_module(self._pypath, parg)
        else:
            self._m = importlib.import_module(self._pypath)


class Injector:
    """
    gere chargement composants engine
    + any engine plugin
    Le fait au moyen dun tableau:
    module name <-> instance of LazyModule
    """

    def __init__(self, module_listing, pack_arg='katagames_engine'):
        self._listing = dict()
        for mname, pypath in module_listing.items():
            obj = ModuleLazyLoader(mname, pypath)
            self._listing[obj.name] = obj
        self._man_set = dict()

        self.package_arg = pack_arg
        self._loading_done = False

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
            tmp = self._listing[item]
            if not tmp.ready:
                self._loading_done = True
                tmp.load_now(self.package_arg)
            return tmp.pymod

    def register(self, sm_name, py_path):
        if self._loading_done:
            print('***warning*** register plugin should be done before using loading elements')
        self._listing[sm_name] = ModuleLazyLoader(sm_name, py_path)
