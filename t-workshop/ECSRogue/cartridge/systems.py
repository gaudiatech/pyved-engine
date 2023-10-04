from . import pimodules
from . import shared
from . import world

import random



__all__ = [
    'pg_event_proces_sys',
    'world_generation_sys',
    'gameover',
    'rendering_sys',
    'physics_sys',
    'ennemyMovement'
]

# aliases
pyv = pimodules.pyved_engine
pyv.bootstrap_e()
Sprsheet = pyv.gfx.Spritesheet
BoolMatrx = pyv.e_struct.BoolMatrix
tileset = None
pg = pyv.pygame
test = None


def pg_event_proces_sys():
    avpos = pyv.find_by_archetype('player')[0]['position']
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pg.K_UP:
                avpos[1] -= 1
                push(1)
            elif ev.key == pg.K_DOWN:
                avpos[1] += 1
                push(3)

            elif ev.key == pg.K_LEFT:
                avpos[0] -= 1
                push(2)

            elif ev.key == pg.K_RIGHT:
                avpos[0] += 1
                push(0)
                
            elif ev.key == pg.K_SPACE:
                # use flag so we we'll reset level, soon in the future
                player = pyv.find_by_archetype('player')[0]
                player['enter_new_map'] = True


def world_generation_sys():
    pl_ent = pyv.find_by_archetype('player')[0]
    monsters = pyv.find_by_archetype('monster')
    potion = pyv.find_by_archetype('potion')[0]
    exit = pyv.find_by_archetype('exit')[0]

    if pl_ent['enter_new_map']:
        pl_ent['enter_new_map'] = False
        print('Level generation...')
        
        w, h = 24, 24
        shared.game_state["rm"] = pyv.rogue.RandomMaze(
            w, h, min_room_size=3, max_room_size=5)
        shared.game_state["visibility_m"] = BoolMatrx((w, h))
        shared.walkable_cells = []
        shared.game_state['visibility_m'].set_all(False)
        pyv.find_by_archetype('player')[0]['position'] = shared.game_state["rm"].pick_walkable_cell()
        world._update_vision(pyv.find_by_archetype('player')[0]['position'][0], pyv.find_by_archetype('player')[0]['position'][1])
        shared.game_state["enemies_pos2type"].clear()
        for monster in monsters :
            pyv.delete_entity(monster)
        for _ in range(5):
            c = shared.game_state['rm'].pick_walkable_cell()
            shared.game_state["enemies_pos2type"][tuple(c)] = 1  # all enemies type=1
            world.create_monster(c)
            
            
        while True:
            exitPos = shared.game_state['rm'].pick_walkable_cell() 
            if exitPos not in [pl_ent.position] + [monster.position for monster in monsters]:
                exit.position = exitPos
                break 
            
        
        while True:
            resultat = random.randint(0, 1)
            potionPos = shared.game_state['rm'].pick_walkable_cell() 
            if potionPos  not in [pl_ent.position] + [monster.position for monster in monsters] + [exit.position ]:
                potion.position = potionPos
                if resultat == 0:
                    potion.effect = 'Heal'
                else :
                    potion.effect = 'Poison'
                break 



def rendering_sys():
    global tileset
    scr = shared.screen
    scr.fill(shared.WALL_COLOR)
    player = pyv.find_by_archetype('player')[0]
    monster = pyv.find_by_archetype('monster')
    

    # ----------
    #  draw tiles
    # ----------
    nw_corner = (0, 0)
    tmp_r4 = [None, None, None, None]
    tuile = shared.TILESET.image_by_rank(912)
    dim = world.get_terrain().get_size()
    for i in range(dim[0]):
        for j in range(dim[1]):
            # ignoring walls
            tmp = world.get_terrain().get_val(i, j)
            if tmp is None:
                continue

            tmp_r4[0], tmp_r4[1] = nw_corner
            tmp_r4[0] += i * shared.CELL_SIDE
            tmp_r4[1] += j * shared.CELL_SIDE
            tmp_r4[2] = tmp_r4[3] = shared.CELL_SIDE
            if not world.can_see((i, j)):  # hidden cell
                
                pg.draw.rect(scr, shared.HIDDEN_CELL_COLOR, tmp_r4)
            else:  # visible tile
                scr.blit(tuile, tmp_r4)
                shared.walkable_cells.append((i, j))


    if shared.end_game_label0:
        lw, lh = shared.end_game_label0.get_size()
        scr.blit(
            shared.end_game_label0, ((shared.SCR_WIDTH-lw)//2, (shared.SCR_HEIGHT-lh)//3)
        )
        scr.blit(
            shared.end_game_label1, ((shared.SCR_WIDTH-lw)//2, (shared.SCR_HEIGHT-lh)//2)
        )
    else:
        # if (player.position[0], player.position[1]) not in shared.walkable_cells:
        #     backmove()
        # ----------
        #  draw player/enemies
        # ----------
        av_i, av_j = pyv.find_by_archetype('player')[0]['position']
        world._update_vision(player.position[0], player.position[1]) ## Update player vision

        ####### EXIT
        
        exit = pyv.find_by_archetype('exit')[0]
        potion = pyv.find_by_archetype('potion')[0]


        if shared.game_state['visibility_m'].get_val(*exit.position):
            scr.blit(shared.TILESET.image_by_rank(1092), (exit.position[0]* shared.CELL_SIDE, exit.position[1]* shared.CELL_SIDE, 32, 32))
        
        if shared.game_state['visibility_m'].get_val(*potion.position):
            if potion.effect == 'Heal':
                scr.blit(shared.TILESET.image_by_rank(810), (potion.position[0]* shared.CELL_SIDE, potion.position[1]* shared.CELL_SIDE, 32, 32))
            elif potion.effect == 'Poison' :
                scr.blit(shared.TILESET.image_by_rank(810), (potion.position[0]* shared.CELL_SIDE, potion.position[1]* shared.CELL_SIDE, 32, 32))
            elif potion.effect == 'disabled':
                scr.blit(tuile, (potion.position[0]* shared.CELL_SIDE, potion.position[1]* shared.CELL_SIDE, 32, 32))



        # fait une projection coordonnées i,j de matrice vers targx, targy coordonnées en pixel de l'écran
        proj_function = (lambda locali, localj: (locali * shared.CELL_SIDE, localj * shared.CELL_SIDE))
        targx, targy = proj_function(av_i, av_j)
        scr.blit(shared.AVATAR, (targx, targy, 32, 32))
        # ----- enemies
        for enemy_info in shared.game_state["enemies_pos2type"].items():
            pos, t = enemy_info
            if not shared.game_state['visibility_m'].get_val(*pos):
                continue
            en_i, en_j = pos[0] * shared.CELL_SIDE, pos[1] * shared.CELL_SIDE
            scr.blit(shared.MONSTER, (en_i, en_j, 32, 32))


def physics_sys():
    player = pyv.find_by_archetype('player')[0]        
    monster = pyv.find_by_archetype('monster')
    exit = pyv.find_by_archetype('exit')[0]  
    potion = pyv.find_by_archetype('potion')[0]  

    for m in monster:
        if player.position == m.position:
            m.health_point -= player.damages
            player.health_point -= m.damages
            print(player.health_point)
            # backmove()
            if m.health_point < 0:
                pyv.delete_entity(m)
                d= shared.game_state["enemies_pos2type"]
                del d[(m.position[0], m.position[1])]
                
    if player.position == exit.position:
        player['enter_new_map'] = True
        shared.level_count +=1
        print('YOU REACHED LEVEL : ' + str(shared.level_count))
        
    
    if player.position == potion.position:
        if potion.effect == 'Heal':
            player.health_point = 100
            print(player.health_point)
            potion.effect = 'disabled'
        elif potion.effect == 'Poison':
            player.health_point -= 20
            print(player.health_point)
            potion.effect = 'disabled'


def push(dir):
    player = pyv.find_by_archetype('player')[0]
    monsters = pyv.find_by_archetype('monster')
    if (player.position[0], player.position[1]) not in shared.walkable_cells :
        print('kick')
        deltas = {
            0: (+1, 0),
            1: (0, -1),
            2: (-1, 0),
            3: (0, +1)
        }
        player.position[0] -= deltas[dir][0]
        player.position[1] -= deltas[dir][1]
        
        
def gameover():
    player = pyv.find_by_archetype('player')[0]  
    classic_ftsize = 38
        
    if player.health_point <= 0 :
        ft = pyv.pygame.font.Font(None, classic_ftsize)
        shared.end_game_label0 = ft.render('Game Over', True, (255, 255, 255), 'black')
        shared.end_game_label1 = ft.render(f'You reached Level : {shared.level_count}' , True, (255, 255, 255), 'black')



def ennemyMovement():
        player = pyv.find_by_archetype('player')[0]  
        testMonster = pyv.find_by_archetype('monster')[0]
        pathfinding_result = pyv.terrain.DijkstraPathfinder.find_path(
            shared.game_state["visibility_m"], testMonster.position,player.position
        )
        # print(pathfinding_result)
        
