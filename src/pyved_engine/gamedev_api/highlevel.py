"""
Pyv API := Ecs func/procedures
  + utility func + pygame constants + the 12 func/procedures defined in the current file

"""
import csv
import re
import time
import uuid
from enum import Enum
from math import degrees as _degrees
from ..compo.MyGameCtrl import MyGameCtrl  # for retro-compatibility
from .. import _hub
from .. import custom_struct as struct
from .. import state_management
from .. import vars
from ..compo import gfx
from ..compo import vscreen
from ..compo.vscreen import flip as _oflip
from ..core import events
from ..core.events import EvManager
from ..core.events import game_events_enum
from ..custom_struct import enum, enum_from_n
from ..state_management import declare_game_states


__all__ = [
    'bootstrap_e', 'close_game', 'curr_state', 'declare_begin', 'declare_end', 'declare_game_states',
    'declare_update', 'draw_circle', 'draw_line', 'draw_polygon', 'draw_rect', 'enum', 'enum_from_n', 'flip',
    'game_events_enum', 'get_ev_manager', 'get_gs_obj', 'get_pressed_keys', 'get_surface', 'init', 'new_font_obj',
    'new_rect_obj', 'preload_assets', 'struct', 'run_game',

    # retro-compat,
    'get_game_ctrl', 'get_ready_flag',

    # new (2024-10)
    'new_actor', 'del_actor', 'post_ev', 'get_curr_world', 'switch_world', 'process_events',

    # const
    'HIGH_RES_MODE', 'LOW_RES_MODE', 'RETRO_MODE'
]


# -------------- actor-based gamedev API (experimental) -------------------------
engine_debug_flag = True
worlds = {"default": {"actors": {}}}
_active_world = "default"
t_last_tick = None


class _Objectifier:
    def __init__(self, data):
        self.__dict__.update(data)


# event system 6
class EventType(Enum):
    LOCAL = "local"
    TO_SERVER = "to_server"
    BROADCAST = "broadcast"


class Mediator:
    def __init__(self, network_layer=None, is_server=False):
        self.listeners = {}  # Dictionary to store listeners for each event type
        self.event_queue = []  # List to store pending events
        self.network_layer = network_layer  # Network layer for server communication
        self.is_server = is_server  # Indicates if this mediator is a server instance
        self.previous_world = None

    def register(self, event_type, listener, actor_id):
        """Registers a listener (callback function) for a specific event type."""
        if event_type not in self.listeners:
            self.listeners[event_type] = {}
        self.listeners[event_type][actor_id] = listener

    def unregister(self, actor_id):
        """Unregisters all listeners for a specific actor."""
        for event_type in list(self.listeners.keys()):
            if actor_id in self.listeners[event_type]:
                del self.listeners[event_type][actor_id]
            if not self.listeners[event_type]:
                del self.listeners[event_type]

    def post(self, event_type, event, cross_type):
        """Posts an event to the event queue, with cross-event type (local, to_server, broadcast)."""
        if not self.network_layer or not cross_type:
            self.event_queue.append((event_type, _Objectifier(event)))  # handle locally
            return

        if not self.is_server:
            # Send the event to the server
            # ??? self.network_layer.send_event(event_type, event)
            self.network_layer.broadcast(event_type, event)
        else:
            # Broadcast to all clients (assuming we have a list of client mediators)
            for client in self.network_layer.get_connected_clients():
                client.post(event_type, event)

    def update(self):
        """Processes the event queue by notifying listeners for each event."""
        cpt = len(self.event_queue)
        while cpt > 0:
            event_type, event = self.event_queue.pop(0)  # Get the next event, the FIFO way
            cpt -= 1
            if event_type not in self.listeners:
                continue

            mapping = self.listeners[event_type].copy()
            for to_whom, callback in mapping.items():
                if to_whom not in worlds[_active_world]['actors']:
                    continue  # world has changed
                adhoc_data = worlds[_active_world]['actors'][to_whom]['data']
                callback(adhoc_data, event)

        if self.previous_world is not None:
            # unregister actors of the current world
            for actor_id in worlds[self.previous_world]["actors"].keys():
                _mediator.unregister(actor_id)
            self.previous_world = None

    # ---------- networking ----------------
    def set_network_layer(self, ref):
        if self.network_layer is not None:
            raise RuntimeError('cannot bind another network layer, one has already be set')
        self.network_layer = ref
        ref.register_mediator(self)


_mediator = Mediator()


def process_events():
    _mediator.update()


def post_ev(evtype, **ev_raw_data):
    if evtype[0] == 'x' and evtype[1] == '_':  # cross event
        _mediator.post(evtype, ev_raw_data, True)  # keep the raw form if we need to push to antother mediator
    else:
        _mediator.post(evtype, ev_raw_data, False)


def list_worlds():
    """Lists all existing world contexts."""
    return list(worlds.keys())


def get_curr_world():
    return _active_world


def switch_world(newworld_name):
    """
    switches to the specified world context. Creates it if it doesn't exist
    """
    global _active_world
    # we do this, to allow the mediator to unregister all actors from previous world, when appropriate
    _mediator.previous_world = _active_world

    # Creating a new world if it doesnt exist
    if newworld_name not in worlds:
        worlds[newworld_name] = {
            "actors": {}
        }
    # switch to the world "newworld_name"
    _active_world = newworld_name
    if engine_debug_flag:
        print('new world:', newworld_name)

    # Let's register back all actors that do exist in this world
    for actor_id, actor_data in worlds[_active_world]["actors"].items():
        if engine_debug_flag:
            print(f're-bind all event handlers for actor {actor_id}')
        # Re-register the actor's event handlers
        for event_type, handler in actor_data["event_handlers"].items():
            _mediator.register(event_type, handler, actor_id)


def delete_world(name):
    """Deletes the specified world context if it is not the currently active one."""
    global _active_world
    if name != _active_world and name in worlds:
        del worlds[name]


def new_actor(local_scope):
    """
    Automatically gathers functions in the local scope that follow the `on_X` naming convention
    (where X can be any combination of letters or underscores), and creates an event_handlers
    dictionary mapping the event types to the functions.

    When calling the function,
    need to provide the local scope via "locals()"
    """
    # Define a regex pattern to match function names starting with 'on_'
    pattern = re.compile(r"on_[A-Za-z_]+")

    # upgrade the data from actor
    packed_data = packing_data(local_scope['data'])

    # setattr(packed_data, 'functions',
    tempfunc = {
        func_name: func
        for func_name, func in local_scope.items()
        if callable(func) and not pattern.match(func_name)
    }

    # Create the event_handlers dictionary by filtering functions that match the pattern
    event_handlers = {
        func_name.replace("on_", ""): func
        for func_name, func in local_scope.items()
        if callable(func) and pattern.match(func_name)
    }

    # Create a unique identifier for the actor
    actor_id = str(uuid.uuid4())
    actor_data = {
        "name": local_scope['actor_type'],
        "data": packed_data,
        "event_handlers": event_handlers,
        "functions": tempfunc
    }
    worlds[_active_world]["actors"][actor_id] = actor_data

    # Register the event handlers
    # TODO need fix?
    for event, handler in event_handlers.items():
        _mediator.register(f"{event}", handler, actor_id)
    # print('creation actor: ', actor_id)

    return actor_id


def del_actor(*args):
    """Unregisters all event handlers and removes the actor from the current world."""
    for actor_id in args:
        if actor_id is None:
            raise ValueError('tried to del_actor, but passed value:None')
        _mediator.unregister(actor_id)
        if actor_id in worlds[_active_world]["actors"]:
            del worlds[_active_world]["actors"][actor_id]
        # print('deletion actor: ', actor_id)


def actor_state(actor_id):
    """Returns the state of the actor with the given ID in the current world."""
    if actor_id is None:
        raise ValueError('passing an actor_id, with value:None')
    if actor_id not in worlds[_active_world]["actors"]:
        return None
    return worlds[_active_world]["actors"].get(actor_id)["data"]


def actor_exec(actor_id, func_name, *extra_args):
    actor_name = worlds[_active_world]["actors"].get(actor_id)["name"]

    # func_table = actor_state_res.functions
    func_table = worlds[_active_world]["actors"].get(actor_id)["functions"]
    # the effective call
    if func_name not in func_table:
        raise SyntaxError(f'cannot find function "{func_name}" for actor "{actor_name}" id:{actor_id}')
    else:
        this_arg = worlds[_active_world]["actors"].get(actor_id)["data"]
        func_table[func_name](this_arg, *extra_args)


def packing_data(given_data):
    return _Objectifier(given_data)


# ------------------------------------------------------------+------------------
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

    from ..foundation.pbackends import build_primalbackend

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


_existing_game_ctrl = None
_ready_flag = False


def init(mode=None, maxfps=None, wcaption=None, forced_size=None, cached_paint_ev=None):
    global _engine_rdy, _upscaling_var, _existing_game_ctrl, _ready_flag
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
    # for retro-compat
    _existing_game_ctrl = MyGameCtrl()
    _ready_flag = True


def get_game_ctrl():
    return _existing_game_ctrl


def get_ready_flag():
    return _ready_flag


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
