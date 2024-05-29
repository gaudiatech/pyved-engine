
screen = None
blocks_pop = None
prev_time_info = None
end_game_label = None  # != None means player cannot move bc he/she lost

# (Size of break-out blocks)
BLOCK_W = 54
BLOCK_H = 30
BLOCK_SPACING = 2
SCR_WIDTH = 960
SCR_HEIGHT = 720
LIMIT = SCR_WIDTH / (BLOCK_W + BLOCK_SPACING)
WALL_X, WALL_Y = 4, 80

# physics
PL_WIDTH, PL_HEIGHT = 110, 25
PLAYER_SPEED = 220
MAX_XSPEED_BALL = 225.0
YSPEED_BALL = 288.0

# ball-related
BALL_INIT_POS = 480, 277
BALL_SIZE = 22
