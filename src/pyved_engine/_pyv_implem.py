from . import _hub
from . import events
from . import state_management as _st_management_module
from . import vars
from .__version__ import ENGI_VERSION as _VER_CST
from .compo import vscreen
from .compo.vscreen import flip as _flip_screen
from .state_management import declare_game_states


# Lets avoid polluting the "pyv.*" namespace and lets make it very clear what's the list
# of functions that are made available when typing "import pyved_engine as pyv" ...
# By adding the following def:

HIGHRES_MODE, RETRO_MODE, LOWRES_MODE = 1, 2, 3

__all__ = [  # the full PYV INTERFACE/API SPECIFICATION
    'bootstrap_e',
    'close_game',
    'declare_game_states',
    'draw_circle',
    'draw_polygon',
    'draw_rect',
    'get_ev_manager',
    'get_game_ctrl',
    'get_surface',
    'get_ready_flag',
    'get_version',
    'init',
    'preload_assets',

    # non callables:
    'HIGHRES_MODE',
    'RETRO_MODE',
    'LOWRES_MODE'
]


# private variables
_ready_flag = False  # if set to True, means that bootstrap_e has been called at least once
_init_flag = False  # if set to True, means the display is active right now
_pyv_backend = None
_ref_pygame = None
_joystick = None
_existing_game_ctrl = None


# -------------------------------
#  private functions AND classes
# -------------------------------
def _screen_param(gfx_mode_code, paintev=None, screen_dim=None):
    global _init_flag
    if isinstance(gfx_mode_code, int) and -1 < gfx_mode_code <= 3:
        if gfx_mode_code == 0 and screen_dim is None:
            ValueError(f'graphic mode 0 required an extra valid screen_dim argument(provided by user: {screen_dim})')

        # from here, we know that the gfx_mode_code is 100% valid
        conventionw, conventionh = vars.disp_size
        if gfx_mode_code != 0:
            adhoc_upscaling = gfx_mode_code
            taille_surf_dessin = int(conventionw / gfx_mode_code), int(conventionh / gfx_mode_code)
        else:
            adhoc_upscaling = 1
            taille_surf_dessin = screen_dim
            print(adhoc_upscaling, taille_surf_dessin)
        # ---------------------------------
        #  legacy code, not modified in july22. It's complex but
        # it works so dont modify unless you really know what you're doing ;)
        # ---------------------------------
        if vscreen.stored_upscaling is None:  # stored_upscaling isnt relevant <= webctx
            _active_state = True
            pygame_surf_dessin = _hub.pygame.display.set_mode(taille_surf_dessin)
            vscreen.set_virtual_screen(pygame_surf_dessin)
        else:

            pygame_surf_dessin = _hub.pygame.surface.Surface(taille_surf_dessin)
            vscreen.set_virtual_screen(pygame_surf_dessin)
            vscreen.set_upscaling(adhoc_upscaling)
            if paintev:
                paintev.screen = pygame_surf_dessin
            if _init_flag:
                return
            _init_flag = True

            if gfx_mode_code:
                pgscreen = _hub.pygame.display.set_mode(vars.disp_size)
            else:
                pgscreen = _hub.pygame.display.set_mode(taille_surf_dessin)
            vscreen.set_realpygame_screen(pgscreen)
    else:
        e_msg = f'graphic mode requested({gfx_mode_code}: {type(gfx_mode_code)}) isnt a valid one! Expected type: int'
        raise ValueError(e_msg)


def _show_ver_infos():
    print(f'KENGI - ver {_VER_CST}, built on top of ')


class _MyGameCtrl(events.EvListener):

    def __init__(self):
        super().__init__()
        self._clock = vars.game_ticker
        self.gameover = False

    def on_gameover(self, ev):
        self.gameover = True

    def loop(self):
        # if state_management.multistate_flag:  # force this, otherwise the 1st state enter method isnt called
        #     self.pev(events.EngineEvTypes.Gamestart)

        while not self.gameover:
            self.pev(events.EngineEvTypes.Update)
            self.pev(events.EngineEvTypes.Paint, screen=vars.screen)
            self._manager.update()
            _flip_screen()
            self._clock.tick(vars.max_fps)


# --------------------------
#  public functions
# --------------------------
def bootstrap_e(print_version=True):
    global _ready_flag, _pyv_backend
    if not _ready_flag:
        _ready_flag = True
        if print_version:
            # skip the msg, (if running KENGI along with katasdk, the sdk has already printed out ver. infos)
            _show_ver_infos()
        # --> init newest event system! in nov22
        # from here and later,
        # we know that kengi_inj has been updated, so we can build a primal backend
        from .foundation.pbackends import build_primalbackend
        _pyv_backend = build_primalbackend(vars.backend_name)  # by default: local ctx
        events.EvManager.instance().a_event_source = _pyv_backend
        # TODO quick fix this part!
        # event.create_manager()
        # _gameticker = event.GameTicker()
        # dry import
        vscreen.cached_pygame_mod = _hub.pygame


def draw_circle(surface, color_arg, position2d, radius, width=0):
    _ref_pygame.draw.circle(surface, color_arg, position2d, radius, width)


def draw_polygon(surface, color_arg, point_li, width=0):
    _ref_pygame.draw.polygon(surface, color_arg, point_li, width)


def draw_rect(surface, color_arg, rect_obj, width=0):
    _ref_pygame.draw.rect(surface, color_arg, rect_obj, width)


def init(gfc_mode=1, caption=None, maxfps=60, screen_dim=None):
    global _joystick, _ref_pygame, _existing_game_ctrl
    bootstrap_e()

    _ref_pygame = _hub.kengi_inj['pygame']
    _ref_pygame.init()
    _ref_pygame.mixer.init()  # activate sounds

    vars.game_ticker = _ref_pygame.time.Clock()
    vars.max_fps = maxfps

    _existing_game_ctrl = _MyGameCtrl()

    jc = _pyv_backend.joystick_count()
    if jc > 0:
        # ------ init the joystick ------
        _joystick = _pyv_backend.joystick_init(0)
        name = _pyv_backend.joystick_info(0)
        print(name + ' detected')
        # numaxes = _joy.get_numaxes()
        # numballs = _joy.get_numballs()
        # numbuttons = _joy.get_numbuttons()
        # numhats = _joy.get_numhats()
        # print(numaxes, numballs, numbuttons, numhats)

    _screen_param(gfc_mode, screen_dim=screen_dim)
    if caption is None:
        caption = f'untitled demo, uses KENGI ver {_VER_CST}'
    _ref_pygame.display.set_caption(caption)


def get_ev_manager():
    return events.EvManager.instance()


def get_game_ctrl():
    global _existing_game_ctrl
    if _existing_game_ctrl is None:
        raise Exception('get_game_ctrl called, while engine is not init.')
    return _existing_game_ctrl


def get_ready_flag():
    global _ready_flag
    return _ready_flag


def get_surface():
    global _init_flag
    if not get_ready_flag():
        raise Exception('calling kengi.get_surface() while the engine isnt ready! (no previous bootstrap op.)')
    if not _init_flag:
        raise Exception('kengi.init has not been called yet')
    return vars.screen


def get_version():
    return _VER_CST


def close_game():
    global _init_flag, _existing_game_ctrl
    vars.screen = None

    vars.images.clear()
    vars.sounds.clear()
    _existing_game_ctrl = None

    if _init_flag:
        _init_flag = False

        if _st_management_module.multistate_flag:
            _st_management_module.multistate_flag = False
            _st_management_module.stack_based_ctrl.turn_off()
            _st_management_module.stack_based_ctrl = None

        if _hub.kengi_inj.is_loaded('ascii') and _hub.ascii.is_ready():
            _hub.ascii.reset()

        events.EvManager.instance().hard_reset()
        vscreen.init2_done = False
        _hub.pygame.mixer.quit()
        _hub.pygame.quit()
