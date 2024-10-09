from . import pimodules
from . import shared


pyv = pimodules.pyved_engine
pyv.bootstrap_e()

__all__ = [
    'controls_sys',
    'physics_sys',
    'rendering_sys',
    'gamectrl_sys',
    'endgame_sys'
]


def interpolate_color(x, y) -> tuple:
    return 150, (x * 0.27) % 256, (y * 1.22) % 256


def controls_sys(dt):
    pg = pyv.pygame
    player = pyv.find_by_archetype('player')[0]
    active_keys = pg.key.get_pressed()
    if active_keys[pg.K_LEFT]:
        player['speed'] = -shared.PLAYER_SPEED
    elif active_keys[pg.K_RIGHT]:
        player['speed'] = shared.PLAYER_SPEED
    else:
        player['speed'] = 0.0


def endgame_sys(dt):
    classic_ftsize = 38
    ball = pyv.find_by_archetype('ball')[0]
    bpy = ball['body'].top
    if bpy > shared.SCR_HEIGHT:
        ft = pyv.pygame.font.Font(None, classic_ftsize)
        shared.end_game_label = ft.render('Game Over', True, (255, 255, 255))

    # has destroyed all blocks
    blocks = pyv.find_by_archetype('block')
    if not len(blocks):  # no more blocks!
        ft = pyv.pygame.font.Font(None, classic_ftsize)
        shared.end_game_label = ft.render('Great job!', True, (255, 255, 255))


def physics_sys(dt):
    if shared.end_game_label is not None:  # block all movements when game over
        return
    # PLAYER MOVEMENT
    player = pyv.find_by_archetype('player')[0]
    px, py = player['body'].topleft
    vx = player['speed']
    plwidth = player['body'].w
    targetx = px + vx * dt
    if not(targetx < 0 or targetx > shared.SCR_WIDTH-plwidth):
        player['body'].x = targetx

    # ##################BALL MOVEMENT
    ball = pyv.find_by_archetype('ball')[0]
    speed_x = ball['speed_X']
    speed_y = ball['speed_Y']
    bpx, bpy = ball['body'].topleft
    ball['body'].x = bpx + dt*speed_x
    ball['body'].y = bpy + dt*speed_y

    if bpx < 0:
        ball['speed_X'] *= -1
        ball['body'].x = 0
    elif ball['body'].right > shared.SCR_WIDTH:
        ball['speed_X'] *= -1
        ball['body'].right = shared.SCR_WIDTH
    if bpy < 0:
        ball['speed_Y'] *= -1
        ball['body'].top = 0

    # ######################Collision
    if player['body'].colliderect(ball['body']):
        ball['body'].bottom = player['body'].top  # stick to the pad
        ball['speed_Y'] *= -1

    # ######################Collision block
    blocks = pyv.find_by_archetype('block')
    for block in blocks:
        if ball['body'].colliderect(block['body']):
            ball['speed_Y'] *= -1
            pyv.delete_entity(block)
            break


def rendering_sys(dt):
    """
    displays everything that can be rendered
    """
    scr = shared.screen
    scr.fill((0, 0, 0))
    li_blocks = pyv.find_by_archetype('block')
    for b in li_blocks:
        pyv.draw_rect(scr, interpolate_color(b['body'][0], b['body'][1]), b['body'])

    pl_ent = pyv.find_by_archetype('player')[0]
    pyv.draw_rect(scr, 'white', pl_ent['body'])

    if shared.end_game_label:
        lw, lh = shared.end_game_label.get_size()
        scr.blit(
            shared.end_game_label, ((shared.SCR_WIDTH-lw)//2, (shared.SCR_HEIGHT-lh)//2)
        )
    else:
        ball = pyv.find_by_archetype('ball')[0]
        pyv.draw_rect(scr, 'blue', ball['body'])


def gamectrl_sys(dt):
    pg = pyv.pygame
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE:
            pyv.vars.gameover = True
