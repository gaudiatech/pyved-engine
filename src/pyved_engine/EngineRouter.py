"""
Pyv API := Ecs func/procedures
  + utility func + pygame constants + the 12 func/procedures defined in the current file

"""
import csv
import json
import os
import time
from io import StringIO
from math import degrees as _degrees
from pyved_engine.sublayer_implem import GameEngineSublayer  # Step 3: Inject the dependency
from . import dep_linking
from . import pe_vars
from . import state_management
from .AssetsStorage import AssetsStorage
from .actors_pattern import Mediator
from .compo import gfx
from .compo import vscreen
from .compo.vscreen import flip as _oflip
from .foundation import events


class EngineRouter:
    """this is basicaly a container to expose the high-level API for the game dev,
    it will be initialized at runtime, before loading a game cartridge so the game dev
    hasn't to worry about that step"""

    # constants that help with engine initialization
    HIGH_RES_MODE, LOW_RES_MODE, RETRO_MODE = 1, 2, 3

    def __init__(self, sublayer_compo: GameEngineSublayer):
        self.debug_mode = False
        self.low_level_service = sublayer_compo
        self.ready_flag = False
        self.storage = AssetsStorage()
        # immediate bind
        self._hub = {
            'SpriteGroup': self.low_level_service.sprite.Group,
            'Sprite': self.low_level_service.sprite.Sprite,
            'sprite_collision': self.low_level_service.sprite.spritecollide
        }
        pe_vars.engine = self

    @staticmethod
    def get_game_ctrl():
        return _existing_game_ctrl

    @staticmethod
    def get_version():
        return pe_vars.ENGINE_VERSION_STR

    def init(self, engine_mode_id: int, maxfps=None, wcaption=None, forced_size=None, cached_paint_ev=None, multistate_info=None) -> None:
        rez = self.low_level_service.fire_up_backend(engine_mode_id)
        self.mediator = Mediator()

        global _engine_rdy, _upscaling_var, _existing_game_ctrl
        if engine_mode_id is None:
            mode = self.HIGH_RES_MODE

        if not _engine_rdy:
            bootstrap_e(maxfps, wcaption)
            print('pyv.init called, but engine hasnt bootstraped yet')
        else:
            print('previous bootstrap_e call detected.')

        # back to times when we used the _hub file
        # _hub.modules_activation()  # bootstrap done so... all good to fire-up pyv modules
        if wcaption:
            dep_linking.pygame.display.set_caption(wcaption)

        if maxfps is None:  # here, we may replace the existing value of maxfps in the engine
            if pe_vars.max_fps:
                pass
            else:
                pe_vars.max_fps = 60
        else:
            pe_vars.max_fps = maxfps

        pe_vars.clock = self.create_clock()

        vscreen.cached_pygame_mod = dep_linking.pygame
        print('setting screen params...')
        _screen_param(engine_mode_id, forced_size, cached_paint_ev)

        # for retro-compat
        if multistate_info:
            _existing_game_ctrl = state_management.StateStackCtrl(*multistate_info)
        else:
            _existing_game_ctrl = state_management.StateStackCtrl()
        # the lines above have replaced class named: MyGameCtrl()
        self.ready_flag = True
        dep_linking.pygame.mixer.init()  # we always enable sounds

    def draw_circle(self, surface, color_arg, position2d, radius, width=0):
        self.low_level_service.draw_circle(surface, color_arg, position2d, radius, width)

    def draw_rect(self, surface, color, rect4, width, **kwargs):
        self.low_level_service.draw_rect(surface, color, rect4, width)

    def draw_line(self, *args, **kwargs):
        self.low_level_service.draw_line(*args, **kwargs)

    def draw_polygon(self, *args, **kwargs):
        self.low_level_service.draw_polygon(*args, **kwargs)

    # --- legit pyved functions
    def bootstrap_e(self):
        self.low_level_service.fire_up_backend(0)  # TODO

        # >>> EXPLICIT
        # from pyved_engine.sublayer_implem import PygameWrapper
        # from pyved_engine import dep_linking

        # a line required so pyv submodules have a direct access to the sublayer, as well
        dep_linking.pygame = self.low_level_service

        # all this should be dynamically loaded?
        from .compo import GameTpl
        from . import custom_struct
        from . import evsys0
        from .looparts import terrain as _terrain
        from .utils import pal
        from . import pe_vars as _vars
        from .foundation.events import game_events_enum
        from . import actors_pattern
        self._hub.update({
            'actors': actors_pattern,
            'game_events_enum': game_events_enum,
            'EvListener': events.EvListener,
            'Emitter': events.Emitter,
            'EngineEvTypes': events.EngineEvTypes,
            'GameTpl': GameTpl.GameTpl,
            'struct': custom_struct,
            'evsys0': evsys0,
            'terrain': _terrain,
            'pal': pal,
            'vars': _vars
        })
        from .looparts import polarbear
        self._hub.update({
            'polarbear': polarbear
        })
        from .looparts import story
        from .looparts import ascii as _ascii
        from .looparts import gui as _gui
        self._hub.update({
            'ascii': _ascii,
            'gui': _gui,
            'story': story,
        })

    def process_evq(self):
        pe_vars.mediator.update()

    def post_ev(self, evtype, **ev_raw_data):
        if self.debug_mode:
            if evtype != 'update' and evtype != 'draw':
                print('>>>>POST', evtype, ev_raw_data)
        if evtype not in pe_vars.omega_events:
            raise ValueError(f'trying to post event {evtype}, but this one hasnt been declared via pyv.setup_evsys6')
        if evtype[0] == 'x' and evtype[1] == '_':  # cross event
            pe_vars.mediator.post(evtype, ev_raw_data, True)  # keep the raw form if we need to push to antother mediator
        else:
            pe_vars.mediator.post(evtype, ev_raw_data, False)

    def get_mouse_coords(self):
        # pygm = _kengi_inj['pygame']
        pygm = dep_linking.pygame
        mpos = pygm.mouse.get_pos()
        # return _kengi_inj['vscreen'].proj_to_vscreen(mpos)
        return vscreen.proj_to_vscreen(mpos)

    def get_surface(self):
        if pe_vars.screen is None:
            raise LookupError('Cannot provide user with a screen ref, since the engine was not initialized!')
        return pe_vars.screen

    def create_clock(self):
        return dep_linking.pygame.time.Clock()

    def get_ev_manager(self):
        return events.EvManager.instance()

    def flip(self):
        _oflip()
        if pe_vars.max_fps:
            pe_vars.clock.tick(pe_vars.max_fps)

    def new_font_obj(self, font_src, font_size: int):  # src can be None!
        return dep_linking.pygame.font.Font(font_src, font_size)

    def new_rect_obj(self, *args):  # probably: x, y, w, h
        return dep_linking.pygame.Rect(*args)

    def close_game(self):
        dep_linking.pygame.quit()

    def close_game(self):
        pe_vars.gameover = False

        self.low_level_service.mixer.quit()
        self.low_level_service.quit()

        self.storage.images.clear()
        self.storage.csvdata.clear()
        self.storage.sounds.clear()
        self.storage.spritesheets.clear()

    def surface_create(self, size):
        return dep_linking.pygame.surface.Surface(size)

    def surface_rotate(self, img, angle):
        return dep_linking.pygame.transform.rotate(img, _degrees(-1 * angle))

    # - deprecated -----------------------------------
    def run_game(self, initfunc, updatefunc, endfunc):
        # TODO this should be deleted
        #  as it wont work in Track- #1 + web
        experimental_webpy = __import__('sys').platform in ('emscripten', 'wasi')
        if not experimental_webpy:  # Track- #1 : the regular execution
            initfunc(None)
            while not pe_vars.gameover:
                # it's assumed that the developer calls pyv.flip, once per frame,
                # without the engine having to take care of that
                updatefunc(time.time())
            endfunc(None)
        else:  # experimental part: for wasm, etc
            import asyncio
            async def async_run_game():
                initfunc(None)
                while not pe_vars.gameover:
                    updatefunc(time.time())
                    self.flip()  # commit gfx mem to screen, already contains the .tick
                    await asyncio.sleep(0)
                endfunc(None)
            asyncio.run(async_run_game())

    # --- trick to use either the hub or the sublayer
    def __getattr__(self, item):
        if item in self._hub:
            return self._hub[item]
        else:
            return getattr(self.low_level_service, item)


# ------------------------------------------------------------+------------------
def get_gs_obj(k):
    return state_management.stack_based_ctrl.get_state_by_code(k)


# vars
_upscaling_var = None
_scr_init_flag = False

# --------------------------------
#  old version
#  need to keep, or we are good ?
# TODO
# def bootstrap_e(maxfps=None, wcaption=None, print_ver_info=True):
#     global _engine_rdy
#     pe_vars.mediator = Mediator()
#
#     if maxfps is None:
#         y = 60
#     else:
#         y = maxfps
#     pe_vars.max_fps = y
#     # in theory the Pyv backend_name can be hacked prior to a pyv.init() call
#     # Now, let's  build a primal backend
#     v = pe_vars.ENGINE_VERSION_STR
#     if print_ver_info:
#         print(f'Booting up pyved-engine {v}...')
#
#     from .foundation.pbackends import build_primalbackend
#
#     # SIDE-EFFECT: Building the backend also sets kengi_inj.pygame !
#     _pyv_backend = build_primalbackend(pe_vars.backend_name)
#     # if you dont call this line below, the modern event system wont work (program hanging)
#     events.EvManager.instance().a_event_source = _pyv_backend
#
#     dep_linking.pygame.init()
#     if wcaption:
#         dep_linking.pygame.display.set_caption(wcaption)
#     _engine_rdy = True


# -------------------------------
#  private functions
# ------------------------------
def _screen_param(gfx_mode_code, screen_dim, cached_paintev) -> None:
    """
    :param gfx_mode_code: either 0 for custom scr_size, or any value in [1, 3] for std scr_size with upscaling
    :param screen_dim: can be None or a pair of integers
    :param cached_paintev: can be None or a pyved event that needs to have its .screen attribute set
    """
    print('---dans screen_params -->')
    print('args:', gfx_mode_code, screen_dim, cached_paintev)
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
    conventionw, conventionh = pe_vars.disp_size
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
        if vscreen.stored_upscaling is not None:
            pygame_surf_dessin = dep_linking.pygame.surface.Surface(taille_surf_dessin)
            vscreen.set_virtual_screen(pygame_surf_dessin)
            vscreen.set_upscaling(adhoc_upscaling)
            if gfx_mode_code:
                pgscreen = dep_linking.pygame.display.set_mode(pe_vars.disp_size)
            else:
                pgscreen = dep_linking.pygame.display.set_mode(taille_surf_dessin)
            vscreen.set_realpygame_screen(pgscreen)

        else:  # stored_upscaling wasnt relevant so far =>we usin webctx
            _active_state = True
            pygame_surf_dessin = dep_linking.pygame.display.set_mode(taille_surf_dessin)
            vscreen.set_virtual_screen(pygame_surf_dessin)
            # this line is useful for enabling mouse_pos computations even in webCtx
            vscreen.stored_upscaling = float(adhoc_upscaling)

        y = pygame_surf_dessin
        pe_vars.screen = y
        if cached_paintev:
            cached_paintev.screen = y
        _scr_init_flag = True


_existing_game_ctrl = None





def curr_state() -> int:
    return state_management.stack_based_ctrl.current


def curr_statename() -> str:
    """
    :returns: a str
    """
    return state_management.stack_based_ctrl.state_code_to_str(
        state_management.stack_based_ctrl.current
    )


# -------
#  september 23 version. It did break upscalin in web ctx
# def flip():
#     global _upscaling_var
#     if _upscaling_var == 2:
#         _hub.pygame.transform.scale(pe_vars.screen, pe_vars.STD_SCR_SIZE, pe_vars.realscreen)
#     elif _upscaling_var == 3:
#         _hub.pygame.transform.scale(pe_vars.screen, pe_vars.STD_SCR_SIZE, pe_vars.realscreen)
#     else:
#         pe_vars.realscreen.blit(pe_vars.screen, (0, 0))
#     _hub.pygame.display.flip()
#     pe_vars.clock.tick(pe_vars.max_fps)
# --------
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
