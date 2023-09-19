from . import shared
from . import pimodules


pyv = pimodules.pyved_engine
pyv.bootstrap_e()

__all__ = [
    'gamectrl_sys',
    'steering_sys',
    'automob_sys',
    'physics_sys',
    'cameratracking_sys',
    'rendering_sys',
    'teleport_sys'
]

worldChange = True


def gamectrl_sys(entities, components):
    pg = pyv.pygame
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE:
            pyv.vars.gameover = True


def steering_sys(entities, components):
    pg = pyv.pygame

    controllable_ent = pyv.find_by_components('controls')
    activekeys = pg.key.get_pressed()

    for ent in controllable_ent:
        ctrl = ent['controls']

        prevup_key_value = ctrl['up']
        prevdown_key_value = ctrl['down']

        ctrl['up'] = activekeys[pg.K_UP]
        ctrl['left'] = activekeys[pg.K_LEFT]
        ctrl['right'] = activekeys[pg.K_RIGHT]
        ctrl['down'] = activekeys[pg.K_DOWN]

        if ctrl['right']:
            ent['speed'][0] = shared.AV_SPEED

        if ctrl['left']:
            ent['speed'][0] = -shared.AV_SPEED

        if not (ctrl['left'] or ctrl['right']):
            ent['speed'][0] = 0.0

        if ent['lower_block']:
            if not prevup_key_value and ctrl['up']:
                ent['accel_y'] -= shared.JUMP_POWER
                ent['lower_block'] = None


def automob_sys(entities, components):
    player = pyv.find_by_archetype('player')[0]

    all_mob_blocks = filter(lambda e: pyv.archetype_of(e) == 'mob_block', entities)
    for mblo in all_mob_blocks:
        k = 0 if mblo['horz_flag'] else 1
        rrect = mblo['body']
        binf, bsup = mblo['bounds']

        if mblo['speed'][k] == 0.0:
            # init the movement
            mblo['speed'][k] = -shared.BLOCK_SPEED
            continue

        adhoc_coord = rrect.x if mblo['horz_flag'] else rrect.y
        if mblo['speed'][k] < 0 and adhoc_coord < binf:
            mblo['speed'][k] *= -1.0
        elif mblo['speed'][k] > 0 and adhoc_coord > bsup:
            mblo['speed'][k] *= -1.0

        # TODO bugfix:
        #  if the BLOCK_SPEED val is too low, the block is static. Howto fix?
        # print('update pos mblock [oldpos]', px, py,'[speed]', vx, vy, '[res]', mblock['body'].topleft)
        if mblo == player['lower_block']:
            if player['lower_block']['horz_flag']:
                player['speed'][0] += mblo['speed'][0]
            else:
                player['speed'][1] = player['lower_block']['speed'][1]


def cameratracking_sys(entities, components):
    pl_ent = pyv.find_by_archetype('player')[0]
    cam_obj = pl_ent['camera']
    if cam_obj.viewport.center != pl_ent['body'].topleft:
        cam_obj.viewport.center = pl_ent['body'].topleft


def physics_sys(entities, components):
    if shared.t_last_update is None:
        dt = 0.0
    else:
        dt = shared.t_now - shared.t_last_update
    shared.t_last_update = shared.t_now

    player = pyv.find_by_archetype('player')[0]

    # player-related
    player['speed'][1] += player['accel_y']
    if abs(player['speed'][1]) > shared.SPEED_CAP:
        sign = -1 if player['speed'][1] < 0 else 1
        player['speed'][1] = sign * shared.SPEED_CAP

    org_x, org_y = player['body'].topleft
    vx, vy = player['speed']
    destx = org_x + vx * dt
    desty = org_y + vy * dt

    # ---------------
    #  collision detection
    # ---------------
    tested_ent = pyv.find_by_archetype('block')
    tested_ent.extend(pyv.find_by_archetype('mob_block'))

    # horizontal
    rtest0 = player['body'].copy()
    rtest0.left = destx
    accepted_x = destx
    for ent_e in tested_ent:
        if rtest0.colliderect(ent_e['body']):
            accepted_x = org_x
            player['speed'][0] = 0.0
            break

    # vertical
    rtest1 = player['body'].copy()
    rtest1.top = desty
    collidor = None
    for ent_e in tested_ent:
        if (pyv.archetype_of(ent_e) != 'player') and rtest1.colliderect(ent_e['body']):
            collidor = ent_e
            break

    # move all mobile blocks
    mob_blocks = pyv.find_by_archetype('mob_block')
    for mblock in mob_blocks:
        vx, vy = mblock['speed']
        px, py = mblock['body'].topleft
        mblock['body'].left = px + vx * dt
        mblock['body'].top = py + vy * dt

    if collidor:
        player['lower_block'] = collidor  # landing somewhere indeed
        vy = player['speed'][1]
        if vy > 0:  # avoid clipping at all costs:
            accepted_y = collidor['body'].top - player['body'].h
        elif vy < 0:
            accepted_y = collidor['body'].bottom+1
        player['speed'][1] = 0.0
        player['accel_y'] = 0.0
    else:
        accepted_y = desty

    player['accel_y'] = player['gravity']
    pb = player['body']
    pb.topleft = (accepted_x, accepted_y)

    # post move: can fall off a cliff
    if player['lower_block']:
        lbb = player['lower_block']['body']
        speedx = player['speed'][0]
        if speedx == 0:
            pass
        elif (speedx > 0 and pb.left > lbb.right) or (speedx < 0 and pb.right < lbb.left):
            if pyv.archetype_of(player['lower_block']) == 'mob_block':
                if player['lower_block']['horz_flag']:
                    player['speed'][0] += -1*player['lower_block']['speed'][0]
            player['lower_block'] = None


def rendering_sys(entities, components):
    """
    displays everything that can be rendered
    """
    scr = shared.screen

    scr.fill((0, 27, 0))

    pl_ent = pyv.find_by_archetype('player')[0]

    cam = pl_ent['camera']

    def disp(scr_ref, ent, color='blue', width=None, img=None):
        cam_relativ_body = ent['body'].copy()
        cam_relativ_body.x -= cam.viewport.x
        cam_relativ_body.y -= cam.viewport.y
        if img:
            scr.blit(img, cam_relativ_body.topleft)
        else:
            pyv.draw_rect(scr, color, cam_relativ_body, width if width else 1)

    # draw player!
    disp(scr, pl_ent, 'red')
    # draw blocks
    li_blocks = pyv.find_by_archetype('block')
    for b in li_blocks:
        disp(scr, b, 'blue')
    mob_blocks = pyv.find_by_archetype('mob_block')
    for b in mob_blocks:
        disp(scr, b, 'orange')

    # draw world edges (need to show where its forbidden to go!)
    a, b = shared.world.limits
    binf_x, binf_y = -a, -b
    bsup_x, bsup_y = a, b
    binf_x -= cam.viewport.x
    bsup_x -= cam.viewport.x
    binf_y -= cam.viewport.y
    bsup_y -= cam.viewport.y
    if 0 < binf_y < cam.viewport.height:
        pyv.draw_line(scr, 'red', (binf_x, binf_y), (bsup_x, binf_y))
    if 0 < bsup_y < cam.viewport.height:
        pyv.draw_line(scr, 'red', (binf_x, bsup_y), (bsup_x, bsup_y))
    # vert
    if 0 < binf_x < cam.viewport.width:
        pyv.draw_line(scr, 'red', (binf_x, binf_y), (binf_x, bsup_y))
    if 0 < bsup_x < cam.viewport.width:
        pyv.draw_line(scr, 'red', (bsup_x, binf_y), (bsup_x, bsup_y))


def _proc_unload_load():
    player = pyv.find_by_archetype('player')[0]
    camref = player['camera']
    pyv.wipe_entities()
    shared.world.load_map(player['next_map'])
    shared.world.create_avatar(camref)


def teleport_sys(entities, components):
    player = pyv.find_by_archetype('player')[0]
    bsup_x, bsup_y = shared.world.limits
    binf_x = -1.0*bsup_x
    binf_y = -1.0*bsup_y
    x, y = player['body'].topleft
    if y <= binf_y or y > bsup_y or x < binf_x or x > bsup_x:
        player['body'].topleft = shared.SPAWN[0], shared.SPAWN[1]
        # reset player speed when he respawns...
        player['speed'][0], player['speed'][1] = [0.0, 0.0]
