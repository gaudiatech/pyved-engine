"""
+-----------------------------------------------------+
| KENGI [K]atagames [ENGI]ne                          |
| Motto ~ Never slow down the innovation              |
|                                                     |
| Main author: wkta-tom (github.com/wkta)             |
|                                                     |
| an open-source project funded by GAUDIA TECH INC.   |
| https://github.com/gaudiatech/kengi                 |
+-----------------------------------------------------+

 * defines a subset of the pygame library (chosen functions & objects)
  and creates a wrapper around it

 * allows for a swift implementation of two essential design patterns:
   Mediator and Model-View-Contoller

 * provides easy access to data structures useful in game development:
   stacks, matrices, trees, graphs, finite state machines, cellular automata

 * provides algorithms that may be tricky to code but are super-useful:
   A-star, Minimax, a FOV algorithm for a 2D grid based world,

 * is extensible: kengi is capable of receiving custom events and custom
  extensions, for example a custom GUI manager, an isometric engine, or
  antything similar, without requiring any architectural change

 * can run along with the KataSDK but can also be detached, to run independently

 * does not know ANYTHING about whether your code runs in a web browser or not,
  although the engine can be hacked to allow such a possibility

 * incentivizes you, the creator, to write clean readable easy-to-refactor &
  easy-to-reuse code!
"""
import time
from . import vars
from abc import ABCMeta, abstractmethod
from ._ecs_pattern import entity, component, EntityManager, System, SystemManager
from . import _hub as hub
from . import pal
from . import struct
from . import tankui
from ._BaseGameState import BaseGameState
from ._hub import Injector
from .compo import vscreen
from .compo import gfx
from .compo.modes import GameModeMger, BaseGameMode
from .compo.vscreen import flip, proj_to_vscreen
from .core import events
from .core.events import Emitter, EvListener, EngineEvTypes, game_events_enum
from .foundation import defs
from .foundation.defs import STD_SCR_SIZE, KengiEv, Singleton
from .foundation.interfaces import PygameIface
from .state_management import declare_game_states
from .util import underscore_format, camel_case_format


# expose all that exists within the pyv interface implementation!!
from ._pyv_implem import *  # check __all__ in the file


class Objectifier:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def get_ev_manager():  # saves some time
    return events.EvManager.instance()


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
        self.clock = None

    @abstractmethod
    def get_video_mode(self):
        raise NotImplementedError

    def list_game_events(self):
        """
        :return: all specific/custom game events
        """
        return None

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
        self.clock = vars.game_ticker  # bind
        self._manager = events.EvManager.instance()
        self._manager.setup(self.list_game_events())
        self._manager.post(EngineEvTypes.Gamestart)  # pushed to notify that we have really started playing

    def update(self, infot):
        pyg = hub.kengi_inj['pygame']
        pk = pyg.key.get_pressed()
        if pk[pyg.K_ESCAPE]:
            self.gameover = True
            return 2, self.nxt_game

        self._manager.post(EngineEvTypes.Update, curr_t=infot)
        self._manager.post(EngineEvTypes.Paint, screen=vscreen.screen)
        self._manager.update()
        flip()
        self.clock.tick(vars.max_fps)

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


class _Config:
    MAXFPS = 45
    SCR_SIZE = (None, None)
    UPSCALING = None  # not defined, yet


config = _Config


# ----------------------------
#  Related to lazy import
# ----------------------------
# this line was here to allow Code Inspection when using legacy API ...
# pyv.pygame.X  auto-completion etc.

# pygame = PygameIface()


def get_injector():
    return hub.kengi_inj


def plugin_bind(plugin_name, pypath):
    hub.kengi_inj.register(plugin_name, pypath)


def bulk_plugin_bind(darg: dict):
    """
    :param darg: association extension(plug-in) name to a pypath
    :return:
    """
    for pname, ppath in darg.items():
        plugin_bind(ppath, ppath)


def __getattr__(attr_name):
    if attr_name in ('ver', 'vernum'):
        return get_version()

    if attr_name == 'Sprite':
        return _hub.pygame.sprite.Sprite

    if get_ready_flag():
        return getattr(hub, attr_name)

    raise AttributeError(f"kengi cannot lazy load, it hasnt bootstrap yet! (user request: {attr_name})")
