import time
from . import shared
from . import pimodules
import os

pyv = pimodules.pyved_engine
pyv.bootstrap_e()

__all__ = [
    'controls_sys',
    'physics_sys',
    'rendering_sys',
    'gamectrl_sys'
]
def interpolate_color(x, y) -> tuple:
    return 150, (x * 0.27) % 256, (y * 1.22) % 256

def controls_sys(entities, components):
    pg = pyv.pygame

    player = pyv.find_by_archetype('player')[0]
    activekeys = pg.key.get_pressed()

    player['left'] = activekeys[pg.K_LEFT]
    player['right'] = activekeys[pg.K_RIGHT]
    if player['right']:
        player['speed'] = shared.PLAYER_SPEED

    if player['left']:
        player['speed'] = -shared.PLAYER_SPEED
            
    if not (player['left'] or player['right']):
        player['speed'] = 0.0
            
def physics_sys(entities, components):
    
    ####################PLAYER MOVEMENT
    player = pyv.find_by_archetype('player')[0]
    pv = player['speed']
    pp = player['body'].topleft
    player['body'].left = pp[0]+pv
    if(player['body'][0]>900 or player['body'][0]<0):
         player['body'].left = pp[0]
         
    ###################BALL MOVEMENT
    ball = pyv.find_by_archetype('ball')[0]
    speed_X = ball['speed_X']
    speed_Y = ball['speed_Y']
    bp = ball['body'].topleft
    ball['body'].left = bp[0] + speed_X
    ball['body'].top = bp[1]+speed_Y

    if(ball['body'][0]>910 or ball['body'][0]<1):
        ball['speed_X'] *= -1.05
    if(ball['body'][1]>720):
        pyv.vars.gameover = True
        print('lose')
    elif(ball['body'][1]<0):
        ball['speed_Y'] *= -1.05

    #######################Collision
        
    if player['body'].colliderect(ball['body']):
        ball['body'].top = bp[1] + speed_Y
        ball['speed_Y'] *= -1.05
        pv *= 1.05

    #######################Collision block
    blocks = pyv.find_by_archetype('block')
    for block in blocks:
        if(ball['body'].colliderect(block['body'])):
            pyv.delete_entity(block)
            ball['body'].top = bp[1]+speed_Y
            ball['speed_Y'] *= -1.05

            

def rendering_sys(entities, components):
    """
    displays everything that can be rendered
    """
    scr = shared.screen

    scr.fill((0, 0, 0))
    pl_ent = pyv.find_by_archetype('player')[0]
    li_blocks = pyv.find_by_archetype('block')
    ball = pyv.find_by_archetype('ball')[0]

    pyv.draw_rect(scr, 'white', pl_ent['body'])
    pyv.draw_rect(scr, 'blue', ball['body'])
    for b in li_blocks:
        pyv.draw_rect(scr, interpolate_color(b['body'][0], b['body'][1]), b['body'])
        
        
def gamectrl_sys(entities, components):
    pg = pyv.pygame
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE:
            pyv.vars.gameover = True