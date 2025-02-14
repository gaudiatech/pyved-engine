"""
Public variables tied to the game engine.

WARNING: Although these variables can be accesed directly, it is NOT recommended
to tweak these values manually.
Unexpected outcomes/side-effects could be produced by doing so.
Instead use functions like pyv.preload_assets(...) or init(max_fps=..., ...) etc.
"""


# below is a read-only value,
# to retrieve this value from outside you can call pyv.get_version()
ENGINE_VERSION_STR = '25.1a1'

DATA_FT_SIZE = 16

# deprecated but mandatory for web ctx
STD_SCR_SIZE = [960, 720]

BASE_ENGINE_EVS = [
    'update', 'draw',
    'mousemotion', 'mouseup', 'mousedown',
    'keyup', 'keydown', 'gameover',
    'conv_begins', 'conv_step', 'conv_finish',  # conversations with npcs
]

bundle_name = None  # set by launcher script

omega_events = list(BASE_ENGINE_EVS)

# - engine related
mediator = None
disp_size = [960, 720]

# engine = None  # to store a reference to the ngine itself. Useful when writing pyv submodules!


backend_name = ''  # type str, and the default value is '' but it could be modified from elsewhere
weblib_sig = None

clock = None  # at some point, this should store a ref on an Obj. typed pygame.time.Clock
max_fps = 45  # will be replaced by whatever is passed to pyv.init(...)
screen = None

# - game related (universal behavior)
# 4 vars in order to handle all game assets
# images = dict()
# fonts = dict()
# spritesheets = dict()
# sounds = dict()
# csvdata = dict()
# data = dict()  # for raw json, most of the time

# 4 vars to handle the game loop conveniently
gameover = False
beginfunc_ref = updatefunc_ref = endfunc_ref = None
