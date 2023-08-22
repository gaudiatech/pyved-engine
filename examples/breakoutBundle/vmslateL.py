

def bootgame(metadata):
    try:
        import vm
        rel_imports = False
    except ModuleNotFoundError:
        from . import vm
        rel_imports = True

    mon_inj = vm.Injector(None)
    mon_inj.set_lazylo_module('pyved_engine', 'pyved_engine')
    mon_inj.set_lazylo_module('math', 'math')
    vm.upwardlink(mon_inj)

    if rel_imports:
        from .cartridge import pimodules
        pimodules.upward_link = mon_inj
        from .cartridge import gamedef
        vm.gameexec(metadata, gamedef)
    else:
        from cartridge import pimodules
        pimodules.upward_link = mon_inj
        from cartridge import gamedef
        vm.gameexec(metadata, gamedef)
