from . import pimodules
from .mvc_parts import NinjamazeMod, NinjamazeView, NinjamazeCtrl, SpecificEvTypes


pyv = pimodules.pyved_engine
EngineEvTypes = pyv.EngineEvTypes


def print_help():
    print('\n' + '*'*32)
    print('This example showcases capabilities of the pyv.rogue')
    print('submodule... You can easily generate a RANDOM MAZE')
    print('you can also use a field-of-view generic algorithm')
    print('to simulate the "fog of war"/unknown parts of the map.')
    print('>>CONTROLS<< SPACE to regen maze | ESCAPE to quit\n' + '*'*32)


@pyv.Singleton
class MiniStorage:
    def __init__(self):
        self.ev_manager = pyv.get_ev_manager()
        self.ev_manager.setup(SpecificEvTypes)
        self.screen = pyv.get_surface()


@pyv.declare_begin
def rogue_begin(vms=None):
    pyv.init(wcaption='roguelike template')
    MiniStorage.instance()  # by doing this, we also init the ev_manager
    m = NinjamazeMod()
    # be careful: you wont be able to instantiate the View if the ev_manager isnt ready
    NinjamazeView(m).turn_on()
    NinjamazeCtrl(m).turn_on()
    print_help()  # so the player knows how to "play"


@pyv.declare_update
def rogue_update(info_t=None):
    gvars = MiniStorage.instance()
    gvars.ev_manager.post(EngineEvTypes.Update, curr_t=info_t)
    gvars.ev_manager.post(EngineEvTypes.Paint, screen=gvars.screen)
    gvars.ev_manager.update()
    pyv.flip()


@pyv.declare_end
def rogue_quit(vms=None):
    pyv.close_game()
    print('bye!')
