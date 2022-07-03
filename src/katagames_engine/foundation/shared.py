
# - shared variables
ctx_emuvram = None
canvas_emuvram = None
canvas_rendering = None
real_pygamescreen = None
screen_rank = 1  # so we can detect whenever its required to update the var in the PAINT engine event
screen = None
special_flip = 0  # flag, set it to 1 when using web ctx
stored_upscaling = 1
