
# const
RUNS_IN_WEB_CTX = '__BRYTHON__' in globals()
CONST_SCR_SIZE = (960, 540)

# variables
screen = None  # ref to Surface

real_pygamescreen = None

canvas_emuvram = None
ctx_emuvram = None

canvas_rendering = None
ctx_rendering = None

stored_upscaling = 1
