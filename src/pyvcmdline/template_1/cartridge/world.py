import random
from . import pimodules
from . import shared


pyv = pimodules.pyved_engine
pygame = pyv.pygame


def player_create():
    player = pyv.new_from_archetype('player')
    pyv.init_entity(player, {
        'speed': 0.0,
        'controls': {'left': False, 'right': False},
        'body': pygame.rect.Rect(shared.SCR_WIDTH//2, 635, shared.PL_WIDTH, shared.PL_HEIGHT)
    })


def ball_create():
    ball = pyv.new_from_archetype('ball')
    if random.choice((True, False)):
        # we select the right dir.
        initial_vx = random.uniform(0.33*shared.MAX_XSPEED_BALL, shared.MAX_XSPEED_BALL)
    else:
        initial_vx = random.uniform(-shared.MAX_XSPEED_BALL, -0.33 * shared.MAX_XSPEED_BALL)
    pyv.init_entity(ball, {
        'speed_X': initial_vx,
        'speed_Y': shared.YSPEED_BALL,
        'body': pygame.rect.Rect(shared.BALL_INIT_POS[0], shared.BALL_INIT_POS[1], shared.BALL_SIZE, shared.BALL_SIZE)
    })


def blocks_create():
    bcy = 0
    for column in range(5):
        bcy = bcy + shared.BLOCK_H + shared.BLOCK_SPACING
        bcx = -shared.BLOCK_W
        for row in range(round(shared.LIMIT)):
            bcx = bcx + shared.BLOCK_W + shared.BLOCK_SPACING
            rrect = pygame.rect.Rect(0 + bcx, 0 + bcy, shared.BLOCK_W, shared.BLOCK_H)
            pyv.init_entity(pyv.new_from_archetype('block'), {
                'body': rrect
            })
