"""
**Never edit that file!**

Its part of the pyved_engine.

The code below is standardized code (required to defined any GameBundleL),
it helps in booting up the internal game cartridge (aka the PyvGC format)

 {{N.B. Tom }}
In general its not recommanded to run that script directly,
 its way better to use `pyv-cli play GameBundleName` ...
 THAT BEING SAID, see the comment at the end of the file
"""


def bootgame(metadata):
    try:
        import vm
        rel_imports = False
    except ModuleNotFoundError:
        from . import vm
        rel_imports = True

    mon_inj = vm.Injector(None)
    mon_inj.set_lazy_loaded_module('pyved_engine', 'pyved_engine')
    mon_inj.set_lazy_loaded_module('math', 'math')
    vm.upward_link(mon_inj)

    if rel_imports:
        from .cartridge import pimodules
        pimodules.upward_link = mon_inj
        from .cartridge import gamedef
        vm.game_execution(metadata, gamedef)
    else:
        from cartridge import pimodules
        pimodules.upward_link = mon_inj
        from cartridge import gamedef
        vm.game_execution(metadata, gamedef)


# I still keep the code below as its handy to allow the script direct execution in rare situations
if __name__ == '__main__':
    import json
    with open('cartridge/metadat.json', 'r') as fp:
        bootgame(json.load(fp))
