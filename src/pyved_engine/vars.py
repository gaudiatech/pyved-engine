"""
Public variables tied to the game engine.

WARNING: Although these variables can be accesed directly, it is NOT recommended
to tweak these values manually.
Unexpected outcomes/side-effects could be produced by doing so.
Instead use functions like pyv.preload_assets(...) or init(max_fps=..., ...) etc.
"""


ENGINE_VERSION_STR = '23.7a1'  # its actually a read-only value, can get it via the func. defined in [pyved_engine.__init__]

backend_name = ''  # type str, and the default value is '' but it could be modified from elsewhere
disp_size = 960, 720
game_ticker = None  # at some point, this should store a ref on an Obj. typed pygame.time.Clock
max_fps = 45  # will be replaced by whatever is passed to pyv.init(...)

images = dict()
sounds = dict()
screen = None
