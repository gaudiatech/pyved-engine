from . import _hub
from . import events
from . import vars
from .__version__ import ENGI_VERSION as _VER_CST
from .compo import vscreen
from . import state_management as _st_management_module


# PYV INTERFACE/API CLEAR SPECIFICATION,
# plus we avoid polluting the [pyv.] namespace
__all__ = [
    # (1) the API
    'bootstrap_e',
    'draw_circle',
    'draw_rect',
    'get_surface',
    'get_ready_flag',
    'get_version',
    'init',
    'preload_assets',
    'quit',
]


# private variables
_ready_flag = False  # if set to True, means that bootstrap_e has been called at least once
_init_flag = False  # if set to True, means the display is active right now
_pyv_backend = None
_ref_pygame = None
_joystick = None


# --------------------------
#  private functions
# --------------------------
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


def draw_rect(surface, color_arg, rect_obj, width=0):
    _ref_pygame.draw.rect(surface, color_arg, rect_obj, width)


def init(gfc_mode=1, caption=None, maxfps=60, screen_dim=None):
    global _joystick, _ref_pygame
    bootstrap_e()

    _ref_pygame = _hub.kengi_inj['pygame']
    _ref_pygame.init()
    _ref_pygame.mixer.init()
    vars.game_ticker = _ref_pygame.time.Clock()
    vars.max_fps = maxfps

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




def get_ready_flag():
    global _ready_flag
    return _ready_flag


def get_surface():
    global _init_flag
    if not get_ready_flag():
        raise Exception('calling kengi.get_surface() while the engine isnt ready! (no previous bootstrap op.)')
    if not _init_flag:
        raise Exception('kengi.init has not been called yet')
    return vscreen.screen


def get_version():
    return _VER_CST


def preload_assets():
    print('dans preload --------------> okéé')


def quit():  # we've kept thi "quit" name because of pygame
    global _init_flag
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
        pyg = _hub.pygame
        pyg.mixer.quit()
        pyg.quit()
