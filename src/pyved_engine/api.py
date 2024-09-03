"""
Pyv API := Ecs func/procedures
  + utility func + pygame constants + the 12 func/procedures defined in the current file

"""

# ----------------------
#  enriching the API
# ----------------------
from ._utility import *
import csv
# ------------------

# does all of this need to be visible from outside? PB: OOP. understanding required
# TODO reflect if this can be rephrased to let go of OOP. without compromising on feature diversity & quantity
from .compo import gfx
from . import pal, state_management  # pal also added so it is includes in the api
from . import custom_struct as struct
from .custom_struct import enum, enum_from_n
import time
from .core import events
from .core.events import game_events_enum
from .state_management import declare_game_states


# const. for init
HIGH_RES_MODE, LOW_RES_MODE, RETRO_MODE = 1, 2, 3

# vars
_engine_rdy = False
_upscaling_var = None
_scr_init_flag = False


# -----------------------
# all imports HERE hav been written only to help us, with the implem of API
# -----------------------
from abc import ABCMeta, abstractmethod
from . import vars
from math import degrees as _degrees
# from .classes import Spritesheet as _Spritesheet
from . import _hub
import time
from .compo import vscreen
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

    @abstractmethod
    def list_game_events(self):
        """
        :return: all specific/custom game events. If nothing applies you can return None or []
        """
        raise NotImplementedError

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
        init(mode=self.get_video_mode())
        self._manager = EvManager.instance()
        self._manager.setup(self.list_game_events())
        self._manager.post(EngineEvTypes.Gamestart)  # pushed to notify that we have really started playing

        gs_enum, mapping = self.list_game_states()

        if gs_enum is not None:
            declare_game_states(gs_enum, mapping, self)

    def update(self, infot):
        pyg = _hub.pygame
        pk = pyg.key.get_pressed()
        if pk[pyg.K_ESCAPE]:
            self.gameover = True
            return 2, self.nxt_game

        self._manager.post(EngineEvTypes.Update, curr_t=infot)
        self._manager.post(EngineEvTypes.Paint, screen=vars.screen)
        self._manager.update()
        flip()

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


# --- exposing draw functions
def draw_line(*args, **kwargs):
    _hub.pygame.draw.line(*args, **kwargs)


def draw_rect(*args, **kwargs):
    _hub.pygame.draw.rect(*args, **kwargs)


def draw_polygon(*args, **kwargs):
    _hub.pygame.draw.polygon(*args, **kwargs)


def draw_circle(surface, color_arg, position2d, radius, width=0):
    _hub.pygame.draw.circle(surface, color_arg, position2d, radius, width)


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
    if __import__('sys').platform in ('emscripten','wasi'):
        import asyncio
        async def async_run_game():
            vars.beginfunc_ref(None)
            while not vars.gameover:
                vars.updatefunc_ref(time.time())
                flip()  # commit gfx mem to screen, already contains the .tick
                await asyncio.sleep(0)
            vars.endfunc_ref(None)

        asyncio.run( async_run_game() )
    else:
        vars.beginfunc_ref(None)
        while not vars.gameover:
            vars.updatefunc_ref(time.time())
            flip()  # commit gfx mem to screen, already contains the .tick
        vars.endfunc_ref(None)
      

# --- rest of functions ---
def preload_assets(adhoc_dict: dict, prefix_asset_folder, prefix_sound_folder, webhack=None):
    """
    expected to find the (mandatory) key 'images',
    also we may find the (optionnal) key 'sounds'
    :param prefix_asset_folder:
    :param adhoc_dict:
    :return:
    """
    from io import StringIO

    print('*'*50)
    print(' CALL to preload assets')
    print('*'*50)
    print()
    for asset_desc in adhoc_dict['asset_list']:

        if isinstance(asset_desc, str):  # either sprsheet or image
            kk = asset_desc.split('.')
            # print('>>>>>charge file:', kk[0], kk[1])
            # print('prefix_asset_folder?', prefix_asset_folder)

            if kk[1] == 'json':

                y = prefix_asset_folder
                if webhack:
                    y = webhack+prefix_asset_folder

                #print("argzz", kk[0], y)
                vars.spritesheets[kk[0]] = gfx.JsonBasedSprSheet(
                    kk[0], pathinfo=y, is_webhack=(webhack is not None)
                )

            elif kk[1] == 'ncsv':
                # filepath = prefix_asset_folder + asset_desc if prefix_asset_folder else asset_desc
                csv_filename = kk[0]+'.'+'ncsv'
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
                filepath = prefix_asset_folder + asset_desc
                print('fetching image:', kk[0], filepath)
                vars.images[kk[0]] = _hub.pygame.image.load(filepath)

    for snd_elt in adhoc_dict['sound_list']:
        k = snd_elt.split('.')[0]
        filepath = prefix_sound_folder + snd_elt
        if webhack is not None:
            filepath = webhack+filepath
        print('fetching the sound:', k, filepath)
        vars.sounds[k] = _hub.pygame.mixer.Sound(filepath)


def bootstrap_e(maxfps=None, wcaption=None, print_ver_info=False):
    global _engine_rdy
    if maxfps is None:
        y = 60
    else:
        y = maxfps
    vars.max_fps = y
    # in theory the Pyv backend_name can be hacked prior to a pyv.init() call
    # Now, let's  build a primal backend
    v = vars.ENGINE_VERSION_STR
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
#  private function
# ------------------------------
def _screen_param(gfx_mode_code, paintev=None, screen_dim=None):
    global _scr_init_flag
    if not (isinstance(gfx_mode_code, int) and -1 < gfx_mode_code <= 3):
        # error management
        e_msg = f'graphic mode requested({gfx_mode_code}: {type(gfx_mode_code)}) isnt a valid one! Expected type: int'
        raise ValueError(e_msg)

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
    if not _scr_init_flag:
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
            if gfx_mode_code:
                pgscreen = _hub.pygame.display.set_mode(vars.disp_size)
            else:
                pgscreen = _hub.pygame.display.set_mode(taille_surf_dessin)
            vscreen.set_realpygame_screen(pgscreen)
        vars.screen = pygame_surf_dessin
        _scr_init_flag = True


def init(maxfps=None, wcaption=None, mode=None):
    global _engine_rdy, _upscaling_var
    if mode is None:
        mode = HIGH_RES_MODE

    if not _engine_rdy:
        bootstrap_e(maxfps, wcaption)
    elif wcaption:
        _hub.pygame.display.set_caption(wcaption)

    vscreen.cached_pygame_mod = _hub.pygame
    _screen_param(mode, screen_dim=None)
    vars.clock = create_clock()


# def proj_to_vscreen(xy_pair):
#     global _upscaling_var
#     if _upscaling_var == 1:
#         return xy_pair
#     else:
#         x, y = xy_pair
#         return x//_upscaling_var, y//_upscaling_var


def close_game():
    _hub.pygame.quit()
    vars.images.clear()
    vars.csvdata.clear()
    vars.sounds.clear()
    vars.spritesheets.clear()
    vars.gameover = False


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
#  restoring an older version of .flip() + proj_to_vscreen
from .compo.vscreen import flip as _oflip
from .compo.vscreen import proj_to_vscreen
def flip():
    _oflip()
    if vars.max_fps:
        vars.clock.tick(vars.max_fps)


def fetch_events():
    return _hub.pygame.event.get()


def get_pressed_keys():
    return _hub.pygame.key.get_pressed()


def load_spritesheet(filepath, tilesize, ck=None):
    obj = _Spritesheet(filepath)
    obj.set_infos(tilesize)
    if ck:
        obj.colorkey = ck  # could be (255, 0, 255) for example
    return obj
