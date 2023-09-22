from . import shared
from . import pimodules


pyv = pimodules.pyved_engine
pyv.bootstrap_e()
pygame = pyv.pygame
Sprsheet = pyv.gfx.Spritesheet


def create_player():
    player = pyv.new_from_archetype('player')
    pyv.init_entity(player, {
        'position': None,
        'controls': {'left': False, 'right': False, 'up': False, 'down': False},
        'damages': 10,
        'health_point': 100,
        'enter_new_map': True
    })


def create_wall():
    wall = pyv.new_from_archetype('wall')
    pyv.init_entity(wall, {})


def create_monster(position):
    monster = pyv.new_from_archetype('monster')
    pyv.init_entity(monster, {
        'body' : position,
        'damages': 10,
        'health_point': 20
    })


def create_exit():
    exit = pyv.new_from_archetype('exit')
    pyv.init_entity(exit, {})


def get_terrain():
    return shared.game_state['rm'].getMatrix()


def _update_vision(i, j):
    if shared.fov_computer is None:
        shared.fov_computer = pyv.rogue.FOVCalc()

    shared.game_state['visibility_m'].set_val(i, j, True)

    def func_visibility(a, b):
        if shared.game_state['visibility_m'].is_out(a, b):
            return False
        if shared.game_state['rm'].getMatrix().get_val(a, b) is None:  # cannot see through walls
            return False
        return True

    li_visible = shared.fov_computer.calc_visible_cells_from(i, j, shared.VISION_RANGE, func_visibility)

    for c in li_visible:
        shared.game_state['visibility_m'].set_val(c[0], c[1], True)


def init_images():
    grid_rez = (32, 32)

    img = pyv.vars.images['tileset']
    tileset = Sprsheet(img, 2)  # use upscaling x2
    tileset.set_infos(grid_rez)

    img = pyv.vars.images['avatar1']
    planche_avatar = Sprsheet(img, 2)  # upscaling x2
    planche_avatar.set_infos(grid_rez)
    planche_avatar.colorkey = (255, 0, 255)

    monster_img = pyv.vars.images['monster']
    monster_img = pygame.transform.scale(monster_img, (32, 32))
    monster_img.set_colorkey((255, 0, 255))
    shared.AVATAR = planche_avatar.image_by_rank(0)
    shared.TILESET = tileset
    shared.MONSTER = monster_img


def can_see(cell):
    # print( shared.game_state['visibility_m'])
    return shared.game_state['visibility_m'].get_val(*cell)

def get_all_walkable_cells():
    w, h = 24, 24  # Update these dimensions to match your map size
    walkable_cells = []

    for i in range(w):
        for j in range(h):
            cell = (i, j)
            walkable_cells.append(cell)

    return walkable_cells
