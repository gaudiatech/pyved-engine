from . import shared
from . import pimodules
import random


pyv = pimodules.pyved_engine

pygame = pyv.pygame


class world:
    
    def create_player():
        player = pyv.new_from_archetype('player')
        pyv.init_entity(player, {
            'speed': 0.0, 
            'controls':{'left': False, 'right': False},
            'body': pygame.rect.Rect(450,600, shared.BLOCK_W, shared.BLOCK_H)
        })
        
    def create_ball():
        ball = pyv.new_from_archetype('ball')
        pyv.init_entity(ball, {
            'speed_X' :random.uniform(-3.0, 3.0), 
            'speed_Y': 5.0, 
            'body': pygame.rect.Rect(shared.BALL_INIT_POS[0],shared.BALL_INIT_POS[1], shared.BALL_SIZE, shared.BALL_SIZE)
        })
        
    def create_blocks():
        bcy = 0 
        LIMIT = 960/(shared.BLOCK_W + shared.BLOCK_SPACING)
        for column in range(5):
            bcy = bcy+shared.BLOCK_H + shared.BLOCK_SPACING
            bcx = -shared.BLOCK_W
            for row in range(round(LIMIT)):
                bcx = bcx +shared.BLOCK_W + shared.BLOCK_SPACING
                rrect = pygame.rect.Rect(0 + bcx, 0 + bcy, shared.BLOCK_W, shared.BLOCK_H)

                pyv.init_entity(pyv.new_from_archetype('block'),{
                    'body': rrect
                })
    
            