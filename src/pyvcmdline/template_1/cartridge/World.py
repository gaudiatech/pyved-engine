from . import pimodules
from . import shared
from .classes import Terrain

pyv = pimodules.pyved_engine
pygame = pyv.pygame


class World:
    """
    modélise tt ce que contient le monde virtuel, on va employer ici que des coordonnées ABSOLUES,
    et du float. L'origine [0, 0] c'est le centre. Donc rien n'empêche d'utiliser des coordonnées négatives
    """

    def __init__(self, glwidth, glheight):
        self._wsize = (glwidth, glheight)
        self._game_objects = list()
        self._platforms = list()
        self.entities = list()

    def link_entity(self, ref_e):
        self.entities.append(ref_e)

    @property
    def limits(self):
        return self._wsize

    @property
    def objects(self):
        return self._game_objects

    def load_map(self, mapname):
        shared.terrain = Terrain(pyv.vars.csvdata[mapname])
        self.add_terrain_blocks(shared.terrain, terrain_origin=[-1324.0, -100.0])

    def create_avatar(self, cam_ref):
        player = pyv.new_from_archetype('player')
        pyv.init_entity(player, {
            'speed': [0.0, 0.0],
            'accel_y': 0.0,
            'gravity': 14.5,
            'lower_block': None,
            'body': pygame.rect.Rect(shared.SPAWN[0], shared.SPAWN[1], shared.AVATAR_SIZE, shared.AVATAR_SIZE),
            'camera': cam_ref,
            'controls': {'up': False, 'down': False, 'left': False, 'right': False}
            })

    def add_game_obj(self, gobj):
        self._game_objects.append(gobj)

    def add_terrain_blocks(self, terrain_obj, terrain_origin=None):
        if terrain_origin is None:
            terrain_origin = [0.0, 0.0]
        basex, basey = terrain_origin

        block_coords_to_btype = dict()
        for j, row in enumerate(terrain_obj.map_data):
            for i, btype in enumerate(row):
                block_coords_to_btype[(i, j)] = btype

        for bcoords, btype in block_coords_to_btype.items():
            bcx, bcy = bcoords
            bcx *= shared.BLOCKSIZE
            bcy *= shared.BLOCKSIZE
            rrect = pygame.rect.Rect(basex + bcx, basey + bcy, shared.BLOCKSIZE, shared.BLOCKSIZE)
            self.add_game_obj(
                {'key': 'block', 'rect': rrect}
            )
            if btype == 1:
                pyv.init_entity(
                    pyv.new_from_archetype('block'), {
                        'body': rrect
                    }
                )
                self._platforms.append(rrect)
            elif btype in (2, 3):
                tmp = (rrect.x if btype == 2 else rrect.y)
                pyv.init_entity(
                    pyv.new_from_archetype('mob_block'), {
                        'body': rrect,
                        'speed': [0.0, 0.0],
                        'bounds': [tmp - shared.BLOCKSIZE*4, tmp],
                        'horz_flag': btype == 2,
                    }
                )
