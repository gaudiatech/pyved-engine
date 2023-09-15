"""
Public variables tied to the game engine.

WARNING: Although these variables can be accesed directly, it is NOT recommended
to tweak these values manually.
Unexpected outcomes/side-effects could be produced by doing so.
Instead use functions like pyv.preload_assets(...) or init(max_fps=..., ...) etc.
"""


ENGINE_VERSION_STR = '23.9a2'  # a read-only value, can this val. from outside via a func. call on pyv.get_version()

# deprecated but mandatory for web ctx
STD_SCR_SIZE = [960, 720]

# - engine related
disp_size = 960, 720
backend_name = ''  # type str, and the default value is '' but it could be modified from elsewhere
weblib_sig = None

clock = None  # at some point, this should store a ref on an Obj. typed pygame.time.Clock
max_fps = 45  # will be replaced by whatever is passed to pyv.init(...)
screen = None

# - game related (universal behavior)
# 4 vars in order to handle all game assets
images = dict()
fonts = dict()
spritesheets = dict()
sounds = dict()
csvdata = dict()

# 4 vars to handle the game loop conveniently
gameover = False
beginfunc_ref = updatefunc_ref = endfunc_ref = None
