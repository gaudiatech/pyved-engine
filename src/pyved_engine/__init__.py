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
from abc import ABCMeta, abstractmethod

from ._ecs_pattern import entity, component, EntityManager, System, SystemManager

from . import _hub as hub
from . import pal
from . import state_management as _state_sm
from . import struct
from . import tankui
from ._BaseGameState import BaseGameState
from .__version__ import ENGI_VERSION as _VER_CST
from ._hub import Injector
from .compo import gfx
from .compo import vscreen
from .compo.modes import GameModeMger, BaseGameMode
from .compo.vscreen import flip, proj_to_vscreen
from .core import events
from .core.events import Emitter, EvListener, EngineEvTypes, game_events_enum
from .foundation import defs
from .foundation.defs import STD_SCR_SIZE, KengiEv, Singleton
from .foundation.interfaces import PygameIface
from .state_management import declare_game_states
from .util import underscore_format, camel_case_format


_active_state = False
_gameticker = None
one_plus_init = False
_stored_kbackend = None
pbackend_name = ''  # can be modified from elsewhere


class Objectifier:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def _show_ver_infos():
    print(f'KENGI - ver {_VER_CST}, built on top of ')


def is_ready():
    global one_plus_init
    return one_plus_init


def bootstrap_e(print_ver_info=True):
    """
    ensure the engine is ready to be used
    :param print_ver_info: bool
    :return:
    """
    global one_plus_init, _gameticker, _stored_kbackend, pbackend_name, pygame
    if one_plus_init:
        return
    del pygame
    one_plus_init = True
    if print_ver_info:
        # skip the msg, (if running KENGI along with katasdk, the sdk has already printed out ver. infos)
        _show_ver_infos()

    # --> init newest event system! in nov22
    # from here and later,
    # we know that kengi_inj has been updated, so we can build a primal backend
    from .foundation.pbackends import build_primalbackend
    _stored_kbackend = build_primalbackend(pbackend_name)  # by default: local ctx
    events.EvManager.instance().a_event_source = _stored_kbackend

    # TODO quick fix this part!
    # event.create_manager()
    # _gameticker = event.GameTicker()

    # dry import
    vscreen.cached_pygame_mod = hub.pygame


def screen_param(gfx_mode_code, paintev=None, screen_dim=None):
    global _active_state, config

    if not isinstance(gfx_mode_code, int) and (1 <= gfx_mode_code <= 3):
        e_msg = f'graphic mode requested({gfx_mode_code}: {type(gfx_mode_code)}) isnt a valid one! Expected type: int'
        raise ValueError(e_msg)

    # from here, we know that the gfx_mode_code is 100% valid
    conventionw, conventionh = STD_SCR_SIZE
    if gfx_mode_code != 0:
        adhoc_upscaling = gfx_mode_code
        taille_surf_dessin = int(conventionw / gfx_mode_code), int(conventionh / gfx_mode_code)
    else:
        if screen_dim is None:
            raise ValueError(f'graphic mode 0 required a valid screen_dim arg (provided by user: {screen_dim})')
        adhoc_upscaling = 1
        taille_surf_dessin = screen_dim

    config.SCR_SIZE = taille_surf_dessin
    config.UPSCALING = adhoc_upscaling

    # ---------------------------------
    #  legacy code, not modified in july22. It's complex but
    # it works so dont modify unless you really know what you're doing ;)
    # ---------------------------------
    if vscreen.stored_upscaling is None:  # stored_upscaling isnt relevant <= webctx
        _active_state = True
        pygame_surf_dessin = hub.pygame.display.set_mode(taille_surf_dessin)
        vscreen.set_virtual_screen(pygame_surf_dessin)
    else:

        pygame_surf_dessin = hub.pygame.surface.Surface(taille_surf_dessin)
        vscreen.set_virtual_screen(pygame_surf_dessin)
        vscreen.set_upscaling(adhoc_upscaling)
        if paintev:
            paintev.screen = pygame_surf_dessin
        if _active_state:
            return
        _active_state = True

        if gfx_mode_code:
            pgscreen = hub.pygame.display.set_mode(STD_SCR_SIZE)
        else:
            pgscreen = hub.pygame.display.set_mode(taille_surf_dessin)
        vscreen.set_realpygame_screen(pgscreen)



_joy = None


def get_surface():
    global _active_state
    if not is_ready():
        raise Exception('calling kengi.get_surface() while the engine isnt ready! (no previous bootstrap op.)')
    if not _active_state:
        raise Exception('kengi.init has not been called yet')
    return vscreen.screen


# TODO repair this part, so it fits kengi v22.11.3+

# def declare_states(gsdefinition, assoc_gscode_cls, mod_glvars=None):
#     global _multistate_flag, state_stack, _stack_based_ctrl
#     _multistate_flag = True
#     state_stack = struct.Stack()
#     _stack_based_ctrl = event.StackBasedGameCtrl(
#         _gameticker, gsdefinition, mod_glvars, assoc_gscode_cls
#     )


class _MyGameCtrl(events.EvListener):
    MAXFPS = 75

    def __init__(self):
        super().__init__()
        self._clock = hub.kengi_inj['pygame'].time.Clock()
        self.gameover = False

    def on_gameover(self, ev):
        self.gameover = True

    def loop(self):
        if state_management.multistate_flag:  # force this, otherwise the 1st state enter method isnt called
            self.pev(events.EngineEvTypes.Gamestart)

        while not self.gameover:
            self.pev(events.EngineEvTypes.Update)
            self.pev(events.EngineEvTypes.Paint, screen=vscreen.screen)
            self._manager.update()
            flip()
            self._clock.tick(self.MAXFPS)


def get_game_ctrl():
    return _MyGameCtrl()


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
    MAXFPS = 75

    def __init__(self):
        self._manager = None
        self.gameover = False
        self.clock = hub.kengi_inj['pygame'].time.Clock()
        self.nxt_game = 'niobepolis'

    @abstractmethod
    def init_video(self):
        raise NotImplementedError

    def setup_ev_manager(self):
        self._manager.setup()

    def enter(self, vms=None):
        """
        Careful if you redefine this:
        one *HAS TO* bind the ev manager to self._manager and call .setup, somehow
        """
        self._manager = events.EvManager.instance()
        self.init_video()
        self.setup_ev_manager()

        # gamestart event HAS TO be pushed so the game rly starts...
        self._manager.post(EngineEvTypes.Gamestart)

    def update(self, infot):
        self._manager.post(EngineEvTypes.Update, curr_t=infot)
        self._manager.post(EngineEvTypes.Paint, screen=vscreen.screen)
        self._manager.update()
        pyg = hub.kengi_inj['pygame']
        pk = pyg.key.get_pressed()
        if pk[pyg.K_ESCAPE] or self.gameover:
            return 2, self.nxt_game
        flip()
        self.clock.tick(self.MAXFPS)

    def exit(self, vms=None):
        quit()

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


# ----------------------------
#  init & quit
# ----------------------------
class _Config:
    MAXFPS = 45
    SCR_SIZE = (None, None)
    UPSCALING = None  # not defined, yet


config = _Config


def init(gfc_mode=1, caption=None, maxfps=60, screen_dim=None):
    global _gameticker, _joy, config
    bootstrap_e()
    config.MAXFPS = int(maxfps)
    pygm = hub.pygame
    pygm.init()
    pygm.mixer.init()

    jc = _stored_kbackend.joystick_count()
    if jc > 0:
        # ------ init the joystick ------
        _joy = _stored_kbackend.joystick_init(0)
        name = _stored_kbackend.joystick_info(0)
        print(name + ' detected')
        # numaxes = _joy.get_numaxes()
        # numballs = _joy.get_numballs()
        # numbuttons = _joy.get_numbuttons()
        # numhats = _joy.get_numhats()
        # print(numaxes, numballs, numbuttons, numhats)

    screen_param(gfc_mode, screen_dim=screen_dim)
    if caption is None:
        caption = f'untitled demo, uses KENGI ver {_VER_CST}'
    pygm.display.set_caption(caption)


def quit():  # we keep the "quit" name bc of pygame
    global _active_state
    if _active_state:
        if _state_sm.multistate_flag:
            _state_sm.multistate_flag = False
            _state_sm.stack_based_ctrl.turn_off()
            _state_sm.stack_based_ctrl = None
        if hub.kengi_inj.is_loaded('ascii') and hub.ascii.is_ready():
            hub.ascii.reset()

        events.EvManager.instance().hard_reset()
        vscreen.init2_done = False
        pyg = get_injector()['pygame']
        pyg.mixer.quit()
        pyg.quit()
        _active_state = False


# ----------------------------
#  Related to lazy import
# ----------------------------
pygame = PygameIface()


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
        return _VER_CST
    if is_ready():
        return getattr(hub, attr_name)
    raise AttributeError(f"kengi cannot lazy load, it hasnt bootstrap yet! (user request: {attr_name})")
