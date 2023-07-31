"""
Pyv API := Ecs func/procedures
  + utility func + pygame constants + the 12 func/procedures defined in the current file

"""

# ----------------------
#  enriching the API
# ----------------------
from ._ecs import *
from ._utility import *
from pygame.constants import *
# ------------------
# does all of this need to be visible from outside? PB: OOP. understanding required
# TODO reflect if this can be rephrased to let go of OOP. without compromising on feature diversity & quantity
from .compo import gfx
from . import pal  # pal also added so it is includes in the api
from . import struct
from .core import events
from .core.events import Emitter, EvListener, EngineEvTypes, game_events_enum
from ._classes import BaseGameState
from .state_management import declare_game_states


# -----------------------
# all imports HERE hav been written only to help us, with the implem of API
# -----------------------
from abc import ABCMeta, abstractmethod
from . import vars
from math import degrees as _degrees
import pygame as _pygame
from .classes import Spritesheet as _Spritesheet
# from . import _hub
import time
from .core.events import EvManager
from .core_classes import Objectifier


# -- enrish with a class
class GameTpl(metaclass=ABCMeta):
    """
    the "no name" game template class. It allows to define your game in a quick way,
    by redefining one or several methods: enter, update, exit
    """
    INFO_STOP_MSG = 'kengi.GameTpl->the loop() call has ended.'
    ERR_LOCK_MSG = 'kengi.GameTpl.loop called while SAFETY_LOCK is on!'
    SAFETY_LOCK = False  # can be set to True from outside, if you don't want a game to call .loop()

    def __init__(self):
        self.gameover = False
        self.nxt_game = 'niobepolis'
        self._manager = None

    @abstractmethod
    def get_video_mode(self):
        raise NotImplementedError

    def list_game_events(self):
        """
        :return: all specific/custom game events
        """
        return None

    def list_game_states(self):
        """
        :return: all specific states(scenes) of the game!
        None, None should be returned as a signal that game doesnt need to use the state manager!
        """
        return None, None

    def enter(self, vms=None):
        """
        Careful if you redefine this:
        one *HAS TO*
         - init video
         - set the gameticker
         - set the _manager attribute (bind the ev manager to self._manager)
         - call self._manager.setup(...) with args
        """
        init(self.get_video_mode())
        self._manager = EvManager.instance()
        self._manager.setup(self.list_game_events())
        self._manager.post(EngineEvTypes.Gamestart)  # pushed to notify that we have really started playing

        gs_enum, mapping = self.list_game_states()

        if gs_enum is not None:
            declare_game_states(gs_enum, mapping, self)

    def update(self, infot):
        pyg = _pygame
        pk = pyg.key.get_pressed()
        if pk[pyg.K_ESCAPE]:
            self.gameover = True
            return 2, self.nxt_game

        self._manager.post(EngineEvTypes.Update, curr_t=infot)
        self._manager.post(EngineEvTypes.Paint, screen=vars.screen)
        self._manager.update()
        flip()
        vars.clock.tick(vars.max_fps)

    def exit(self, vms=None):
        close_game()

    def loop(self):
        """
        its forbidden to call .loop() in the web ctx, but its convenient in the local ctx
        if one wants to test a program without using the Kata VM
        :return:
        """
        # lock mechanism, for extra safety so we never call .loop() in the web ctx
        if self.SAFETY_LOCK:
            raise ValueError(self.ERR_LOCK_MSG)

        # use enter, update, exit to handle the global "run game logic"
        self.enter()

        while not self.gameover:
            infot = time.time()
            self.update(infot)
        self.exit()
        print(self.INFO_STOP_MSG)


# --- enrich with functions
draw_line = _pygame.draw.line
draw_polygon = _pygame.draw.polygon


# --------------
#  3 decorators + the game_exec func to make gameloops standardized
# --------------
def declare_begin(gfunc):  # decorator!
    vars.beginfunc_ref = gfunc
    return gfunc


def declare_update(gfunc):  # decorator!
    vars.updatefunc_ref = gfunc
    return gfunc


def declare_end(gfunc):  # decorator!
    vars.endfunc_ref = gfunc
    return gfunc


def run_game():
    vars.beginfunc_ref()
    while not vars.gameover:
        vars.updatefunc_ref()
        flip()  # commit gfx mem to screen
        vars.clock.tick(vars.max_fps)
    vars.endfunc_ref()


# --- rest of functions ---
def preload_assets(adhoc_dict: dict, prefix_asset_folder=None):
    """
    expected to find the (mandatory) key 'images',
    also we may find the (optionnal) key 'sounds'
    :param prefix_asset_folder:
    :param adhoc_dict:
    :return:
    """
    for gfx_elt in adhoc_dict['images']:
        filepath = gfx_elt if (prefix_asset_folder is None) else prefix_asset_folder + gfx_elt
        vars.images[gfx_elt.split('.')[0]] = _pygame.image.load(filepath)

    if 'sounds' in adhoc_dict:
        for snd_elt in adhoc_dict['sounds']:
            filepath = snd_elt if (prefix_asset_folder is None) else prefix_asset_folder + snd_elt
            vars.sounds[snd_elt.split('.')[0]] = _pygame.mixer.Sound(filepath)


def init(opt_arg=None):
    # in theory the Pyv backend_name can be hacked prior to a pyv.init() call
    # Now, let's  build a primal backend
    v = vars.ENGINE_VERSION_STR
    print(f'pyved-engine {v}')

    from .foundation.pbackends import build_primalbackend
    _pyv_backend = build_primalbackend(vars.backend_name)

    # if you dont call this line below, the modern event system wont work (program hanging)
    events.EvManager.instance().a_event_source = _pyv_backend
    _pygame.init()

    vars.screen = create_screen(vars.disp_size)
    vars.clock = create_clock()


# TODO repair that feature
def proj_to_vscreen(xy_pair):
    return xy_pair


def close_game():
    _pygame.quit()

    vars.images.clear()
    vars.sounds.clear()

    vars.gameover = False


def create_clock():
    return _pygame.Clock()


def get_ev_manager():
    return EvManager.instance()


def create_screen(scr_size=None):
    if scr_size is None:
        scr_size_arg = (960, 720)
    else:
        scr_size_arg = scr_size
    vars.screen = _pygame.display.set_mode(scr_size_arg)
    return vars.screen


def get_surface():
    if vars.screen is None:
        raise LookupError('Cannot provide user with a screen ref, since the engine was not initialized!')
    return vars.screen


def surface_create(size):
    return _pygame.surface.Surface(size)


def surface_rotate(img, angle):
    return _pygame.transform.rotate(img, _degrees(-1 * angle))


def flip():
    return _pygame.display.flip()


def fetch_events():
    return _pygame.event.get()


def get_pressed_keys():
    return _pygame.key.get_pressed()


def load_spritesheet(filepath, tilesize, ck=None):
    obj = _Spritesheet(filepath)
    obj.set_infos(tilesize)
    if ck:
        obj.colorkey = ck  # could be (255, 0, 255) for example
    return obj