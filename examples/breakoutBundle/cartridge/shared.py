import random


screen = None
blocks_pop = None

# (Size of break-out blocks)
BLOCK_W = 54
BLOCK_H = 30
BLOCK_SPACING = 2
WALL_X, WALL_Y = 4, 80
PLAYER_SPEED = 10

# ball-related
BALL_INIT_POS = 480, 277
BALL_SIZE = 22
RANDOM_DIR = random.uniform(-5.0, 5.0)

