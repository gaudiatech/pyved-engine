"""
Pyv API := Ecs func/procedures
  + utility func + pygame constants + the 12 func/procedures defined in the current file

"""
import csv
import time
from math import degrees as _degrees

from . import _hub
from . import custom_struct as struct
from . import state_management
from . import vars
from .compo import gfx
from .compo import vscreen
from .compo.vscreen import flip as _oflip
from .core import events
from .core.events import EvManager
from .core.events import game_events_enum
from .custom_struct import enum, enum_from_n
from .state_management import declare_game_states


__all__ = [
    'bootstrap_e', 'close_game', 'curr_state', 'declare_begin', 'declare_end', 'declare_game_states',
    'declare_update', 'draw_circle', 'draw_line', 'draw_polygon', 'draw_rect', 'enum', 'enum_from_n', 'flip',
    'game_events_enum', 'get_ev_manager', 'get_gs_obj', 'get_pressed_keys', 'get_surface', 'init', 'new_font_obj',
    'new_rect_obj', 'preload_assets', 'struct', 'run_game',
    # const
    'HIGH_RES_MODE', 'LOW_RES_MODE', 'RETRO_MODE'
]


def get_gs_obj(k):
    return state_management.stack_based_ctrl.get_state_by_code(k)


# const. for init
HIGH_RES_MODE, LOW_RES_MODE, RETRO_MODE = 1, 2, 3

# vars
_engine_rdy = False
_upscaling_var = None
_scr_init_flag = False


# --- exposing draw functions
def draw_line(*args, **kwargs):
    _hub.pygame.draw.line(*args, **kwargs)


def draw_rect(*args, **kwargs):
    _hub.pygame.draw.rect(*args, **kwargs)


def draw_polygon(*args, **kwargs):
    _hub.pygame.draw.polygon(*args, **kwargs)


def draw_circle(surface, color_arg, position2d, radius, width=0):
    _hub.pygame.draw.circle(surface, color_arg, position2d, radius, width)


def new_font_obj(font_src, font_size: int):  # src can be None!
    return _hub.pygame.font.Font(font_src, font_size)


def new_rect_obj(*args):  # probably: x, y, w, h
    return _hub.pygame.Rect(*args)


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
    # special case for pygbag or something similar:
    if __import__('sys').platform in ('emscripten', 'wasi'):
        import asyncio

        async def async_run_game():
            vars.beginfunc_ref(None)
            while not vars.gameover:
                vars.updatefunc_ref(time.time())
                flip()  # commit gfx mem to screen, already contains the .tick
                await asyncio.sleep(0)
            vars.endfunc_ref(None)

        asyncio.run(async_run_game())
        return

    vars.beginfunc_ref(None)
    while not vars.gameover:
        # it is assumed that the developer calls pyv.flip,
        # once per frame,
        # without the engine having to take care of that
        vars.updatefunc_ref(time.time())
    vars.endfunc_ref(None)


# --- rest of functions ---
def preload_assets(adhoc_dict: dict, prefix_asset_folder, prefix_sound_folder, webhack=None):
    """
    expected to find the (mandatory) key 'images',
    also we may find the (optionnal) key 'sounds'
    :param webhack:
    :param prefix_sound_folder:
    :param prefix_asset_folder:
    :param adhoc_dict:
    :return:
    """
    from io import StringIO

    print('*' * 50)
    print(' CALL to preload assets')
    print('*' * 50)
    print()
    for asset_desc in adhoc_dict['asset_list']:

        if isinstance(asset_desc, str):  # either sprsheet or image
            kk = asset_desc.split('.')
            # print('>>>>>charge file:', kk[0], kk[1])
            # print('prefix_asset_folder?', prefix_asset_folder)

            if kk[1] == 'json':

                y = prefix_asset_folder
                if webhack:
                    y = webhack + prefix_asset_folder
                adhocv = None
                if webhack:
                    if prefix_asset_folder == './':
                        adhocv = ''
                    else:
                        adhocv = prefix_asset_folder
                vars.spritesheets[kk[0]] = gfx.JsonBasedSprSheet(
                    kk[0], pathinfo=y, is_webhack=adhocv
                )

            elif kk[1] == 'ncsv':
                # filepath = prefix_asset_folder + asset_desc if prefix_asset_folder else asset_desc
                csv_filename = kk[0] + '.' + 'ncsv'
                if webhack:
                    y = webhack + csv_filename
                else:
                    y = prefix_asset_folder + csv_filename
                with open(y, 'r') as file:
                    # csvreader = csv.reader(file)
                    str_csv = file.read()
                    f = StringIO(str_csv)
                    map_data = list()
                    reader = csv.reader(f, delimiter=',')
                    for row in reader:
                        if len(row) > 0:
                            map_data.append(list(map(int, row)))
                    vars.csvdata[kk[0]] = map_data

            elif kk[1] == 'ttf':  # a TTF font
                key = "custom_ft"
                ft_size = 22
                ft_filename = asset_desc

                if webhack:
                    y = webhack + ft_filename
                else:
                    y = prefix_asset_folder + ft_filename
                print('fetching font:', key, ft_filename, f'[{y}]')
                vars.fonts[key] = _hub.pygame.font.Font(
                    y,
                    ft_size
                )

            else:  # necessarily an image
                if prefix_asset_folder == './':
                    filepath = asset_desc
                else:
                    filepath = prefix_asset_folder + asset_desc
                print('fetching image:', kk[0], filepath)
                vars.images[kk[0]] = _hub.pygame.image.load(filepath)

    for snd_elt in adhoc_dict['sound_list']:
        k = snd_elt.split('.')[0]
        filepath = prefix_sound_folder + snd_elt
        if webhack is not None:
            filepath = webhack + filepath
        print('fetching the sound:', k, filepath)
        vars.sounds[k] = _hub.pygame.mixer.Sound(filepath)


def bootstrap_e(maxfps=None, wcaption=None, print_ver_info=True):
    global _engine_rdy
    if maxfps is None:
        y = 60
    else:
        y = maxfps
    vars.max_fps = y
    # in theory the Pyv backend_name can be hacked prior to a pyv.init() call
    # Now, let's  build a primal backend
    v = vars.ENGINE_VERSION_STR
    if print_ver_info:
        print(f'Booting up pyved-engine {v}...')

    from .foundation.pbackends import build_primalbackend

    # SIDE-EFFECT: Building the backend also sets kengi_inj.pygame !
    _pyv_backend = build_primalbackend(vars.backend_name)
    # if you dont call this line below, the modern event system wont work (program hanging)
    events.EvManager.instance().a_event_source = _pyv_backend

    _hub.pygame.init()
    if wcaption:
        _hub.pygame.display.set_caption(wcaption)
    _engine_rdy = True


# -------------------------------
#  private functions
# ------------------------------
def _screen_param(gfx_mode_code, screen_dim, cached_paintev) -> None:
    """
    :param gfx_mode_code: either 0 for custom scr_size, or any value in [1, 3] for std scr_size with upscaling
    :param screen_dim: can be None or a pair of integers
    :param cached_paintev: can be None or a pyved event that needs to have its .screen attribute set
    """
    global _scr_init_flag

    # all the error management tied to the "gfx_mode_code" argument has to be done now
    is_valid_gfx_mode = isinstance(gfx_mode_code, int) and 0 <= gfx_mode_code <= 3
    if not is_valid_gfx_mode:
        info_t = type(gfx_mode_code)
        err_msg = f'graphic mode-> {gfx_mode_code}: {info_t}, isnt valid one! Expected type: int'
        raise ValueError(err_msg)
    if gfx_mode_code == 0 and screen_dim is None:
        ValueError(f'Error! Graphic mode 0 implies that a valid "screen_dim" argument is provided by the user!')

    # from here and below,
    # we know the gfx_mode_code is valid 100%
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
    if not _scr_init_flag:
        if vscreen.stored_upscaling is None:  # stored_upscaling isnt relevant <= webctx
            _active_state = True
            pygame_surf_dessin = _hub.pygame.display.set_mode(taille_surf_dessin)
            vscreen.set_virtual_screen(pygame_surf_dessin)
        else:
            pygame_surf_dessin = _hub.pygame.surface.Surface(taille_surf_dessin)
            vscreen.set_virtual_screen(pygame_surf_dessin)
            vscreen.set_upscaling(adhoc_upscaling)
            if gfx_mode_code:
                pgscreen = _hub.pygame.display.set_mode(vars.disp_size)
            else:
                pgscreen = _hub.pygame.display.set_mode(taille_surf_dessin)
            vscreen.set_realpygame_screen(pgscreen)

        y = pygame_surf_dessin
        vars.screen = y
        if cached_paintev:
            cached_paintev.screen = y
        _scr_init_flag = True


def init(mode=None, maxfps=None, wcaption=None, forced_size=None, cached_paint_ev=None):
    global _engine_rdy, _upscaling_var
    if mode is None:
        mode = HIGH_RES_MODE
    if _engine_rdy:
        if wcaption:
            _hub.pygame.display.set_caption(wcaption)
    else:
        bootstrap_e(maxfps, wcaption)
    vscreen.cached_pygame_mod = _hub.pygame
    _screen_param(mode, forced_size, cached_paint_ev)
    vars.clock = create_clock()


# def proj_to_vscreen(xy_pair):
#     global _upscaling_var
#     if _upscaling_var == 1:
#         return xy_pair
#     else:
#         x, y = xy_pair
#         return x//_upscaling_var, y//_upscaling_var


def close_game():
    vars.gameover = False
    _hub.pygame.quit()
    vars.images.clear()
    vars.csvdata.clear()
    vars.sounds.clear()
    vars.spritesheets.clear()


def create_clock():
    return _hub.pygame.time.Clock()


def get_ev_manager():
    return EvManager.instance()


def curr_state() -> int:
    return state_management.stack_based_ctrl.current


def curr_statename() -> str:
    """
    :returns: a str
    """
    return state_management.stack_based_ctrl.state_code_to_str(
        state_management.stack_based_ctrl.current
    )


def get_surface():
    if vars.screen is None:
        raise LookupError('Cannot provide user with a screen ref, since the engine was not initialized!')
    return vars.screen


def surface_create(size):
    return _hub.pygame.surface.Surface(size)


def surface_rotate(img, angle):
    return _hub.pygame.transform.rotate(img, _degrees(-1 * angle))


# -------
#  september 23 version. It did break upscalin in web ctx
# def flip():
#     global _upscaling_var
#     if _upscaling_var == 2:
#         _hub.pygame.transform.scale(vars.screen, vars.STD_SCR_SIZE, vars.realscreen)
#     elif _upscaling_var == 3:
#         _hub.pygame.transform.scale(vars.screen, vars.STD_SCR_SIZE, vars.realscreen)
#     else:
#         vars.realscreen.blit(vars.screen, (0, 0))
#     _hub.pygame.display.flip()
#     vars.clock.tick(vars.max_fps)
# --------


def flip():
    _oflip()
    if vars.max_fps:
        vars.clock.tick(vars.max_fps)


def fetch_events():
    return _hub.pygame.event.get()


def get_pressed_keys():
    return _hub.pygame.key.get_pressed()


# - deprecated
# def load_spritesheet(filepath, tilesize, ck=None):
#     obj = _Spritesheet(filepath)
#     obj.set_infos(tilesize)
#     if ck:
#         obj.colorkey = ck  # could be (255, 0, 255) for example
#     return obj
