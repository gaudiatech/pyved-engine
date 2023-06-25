"""
public variables tied to the game engine.
WARNING: Although these variables can be accesed directly, it is NOT recommended
to tweak these values manually. Unexpected outcomes/side-effects could be produced
"""

backend_name = ''  # type str, and the default value is '' but it could be modified from elsewhere
disp_size = 960, 720
game_ticker = None  # at some point, this should store a ref on an Obj. typed pygame.time.Clock
