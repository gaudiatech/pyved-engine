import csv
from io import StringIO
from . import pimodules
from . import shared

pyv = pimodules.pyved_engine
pygame = pyv.pygame


class Camera:
    TILE_SIZE = 32

    def __init__(self, position, world_ref):
        x, y = position
        self.viewport = pygame.Rect(x, y, shared.WIDTH, shared.HEIGHT)
        self.width = shared.WIDTH
        self.height = shared.HEIGHT
        self.world = world_ref

        for obj in self.world.objects:
            if obj['key'] == 'player':
                self.player = obj['ref']
                break

        self.screen_center_x = self.width // 2
        self.screen_center_y = self.height // 2
        self.tracked_object = None

    def move(self, dx, dy):
        self.viewport.x += dx
        self.viewport.y += dy

    def draw_map(self, screen):
        player_x = self.player.character_x
        offset_x = self.screen_center_x - player_x * self.TILE_SIZE
        screen.blit(self.terrain.background_image, (0, 0))

        for y, row in enumerate(self.terrain.map_data):
            for x, tile in enumerate(row):
                image = self.terrain.tile_images.get(tile, None)
                if image:
                    xc, yc = self.viewport.topleft
                    screen.blit(image, (x * self.TILE_SIZE + xc, y * self.TILE_SIZE + yc))


# class Projectile:
#     def __init__(self, x, y, direction):
#         self.x = x
#         self.y = y
#         self.direction = direction
#         self.speed = 15.0
#         self.active = True
#
#     def update(self, terrain):
#         if self.active:
#             if self.direction == 'left':
#                 new_x = self.x - self.speed * terrain.clock.get_time() / 1000.0
#             else:
#                 new_x = self.x + self.speed * terrain.clock.get_time() / 1000.0
#             if terrain.is_collision(new_x, self.y):
#                 self.active = False
#             else:
#                 self.x = new_x


class Terrain:
    SAFETY_CNT = 0

    def __init__(self, mapdata):
        self.SAFETY_CNT += 1
        if self.SAFETY_CNT > 1:
            raise ValueError('2nd instance of terrain')
        self.map_data = mapdata  #self.parse_map(scsv)

        self.row_tile_counts = [len(row) for row in self.map_data]
        self.clock = pygame.time.Clock()
        self.game_over = False

        self.collidable_tiles = {'x', 'y'}
        self.screen_center_x = shared.WIDTH // 2
        self.screen_center_y = shared.HEIGHT // 2


# class Player:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#         self.projectiles = []
#         self.max_projectiles = 5

    # def shoot(self):
    #     if len(self.projectiles) < self.max_projectiles:
    #         if self.character_vel_x < 0:
    #             direction = 'left'
    #         elif self.character_vel_x > 0:
    #             direction = 'right'
    #         else:
    #             direction = self.oldDirection
    #         projectile = Projectile(self.character_x, self.character_y, direction)
    #         self.projectiles.append(projectile)

    # def update(self):
    #     for projectile in self.projectiles:
    #         projectile.update(self.terrain)
    #         if not projectile.active:
    #             self.projectiles.remove(projectile)
