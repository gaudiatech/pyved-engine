import math

import pyved_engine as pyv
from demo_entities import Player


class SysInput(pyv.System):
    def __init__(self, entities):
        self.gameover = False
        self.entities = entities

    def proc(self):
        pygame = pyv.pygame
        pl_obj = next(self.entities.get_by_class(Player))

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.gameover = True

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.gameover = True
                elif ev.key == pygame.K_SPACE:
                    pl_obj.style = (pl_obj.style + 1) % 3
                else:
                    if ev.key == pygame.K_UP:
                        pl_obj.thrust = +2.845
                    if ev.key == pygame.K_DOWN:
                        pl_obj.thrust = pl_obj.thrust/2
                    if ev.key == pygame.K_LEFT:
                        pl_obj.delta_angle = -0.1
                    if ev.key == pygame.K_RIGHT:
                        pl_obj.delta_angle = 0.1

            elif ev.type == pygame.KEYUP:
                pl_obj = next(self.entities.get_by_class(Player))
                tmp = pygame.key.get_pressed()
                if not tmp[pygame.K_DOWN] and not tmp[pygame.K_UP]:
                    pl_obj.vy = 0
                if not tmp[pygame.K_LEFT] and (not tmp[pygame.K_RIGHT]):
                    pl_obj.delta_angle = 0


class SysEntityMover(pyv.System):
    def __init__(self, ent):
        self.entities = ent

    def proc(self):
        pl_obj = next(self.entities.get_by_class(Player))
        if pl_obj.delta_angle != 0:
            pl_obj.angle = pl_obj.angle+pl_obj.delta_angle

        if pl_obj.thrust > 10**-1:
            # compute a Speed 2-Vector, based on angle+thrust
            speedvector = pyv.pygame.math.Vector2()
            speedvector.from_polar((1, math.degrees(pl_obj.angle)))
            speedvector.x *= pl_obj.thrust
            speedvector.y *= pl_obj.thrust

            # update x,y values
            pl_obj.x += speedvector.x
            pl_obj.y += speedvector.y

            # clamp coords!
            xcap, ycap = pyv.vars.screen.get_size()
            if pl_obj.x < 0:
                pl_obj.x += xcap
            elif pl_obj.x >= xcap:
                pl_obj.x -= xcap

            if pl_obj.y < 0:
                pl_obj.y += ycap
            elif pl_obj.y >= ycap:
                pl_obj.y -= ycap


class SysView2D(pyv.System):
    BG_COLOR = '#787878'
    SHIP_COLOR = '#22feb4'
    RAD = 17

    def __init__(self, entities, screen):
        self.entities = entities
        self.screen = screen

        self.player_img = pyv.gfx.Spritesheet('topdown-shooter-spritesheet.png')
        self.player_img.set_infos((32, 32))
        self.player_img.colorkey = (0, 0, 0)

    def _draw_player(self):
        pass
        # surf = self.screen
        # pmath = pyv.pygame.math
        #
        # # fetch player pos & orientation
        # pl_obj = next(self.entities.get_by_class(Player))
        # pt_central = (pl_obj.x, pl_obj.y)
        # orientation = pl_obj.angle
        #
        # tv = [
        #     pmath.Vector2(),
        #     pmath.Vector2(),
        #     pmath.Vector2()
        # ]
        # tv[0].from_polar((self.RAD * 1.25, math.degrees(orientation + (2.0 * math.pi / 3))))
        # tv[1].from_polar((self.RAD * 3, math.degrees(orientation)))
        # tv[2].from_polar((self.RAD * 1.25, math.degrees(orientation - (2.0 * math.pi / 3))))
        # pt_li = [
        #     pmath.Vector2(*pt_central),
        #     pmath.Vector2(*pt_central),
        #     pmath.Vector2(*pt_central)
        # ]
        # for i in range(3):
        #     pt_li[i] += tv[i]
        #
        # pyv.draw_polygon(surf, self.SHIP_COLOR, pt_li, 2)

    # @staticmethod
    # def rot_center(image, angle):
    #     """rotate an image while keeping its center and size"""
    #     orig_rect = image.get_rect()
    #     rot_image = pyv.pygame.transform.rotate(image, angle)
    #     rot_rect = orig_rect.copy()
    #     rot_rect.center = rot_image.get_rect().center
    #     rot_image = rot_image.subsurface(rot_rect).copy()
    #     return rot_image

    @staticmethod
    def blitRotateCenter(surf, image, topleft, angle):
        rotated_image = pyv.pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)
        surf.blit(rotated_image, new_rect)

    def _draw_player(self):
        pl_obj = next(self.entities.get_by_class(Player))
        pt_central = (pl_obj.x, pl_obj.y)
        orientation = -math.degrees(pl_obj.angle)

        self.blitRotateCenter(self.screen, self.player_img.image_by_rank(pl_obj.style), pt_central, orientation)

    def proc(self):
        self.screen.fill(self.BG_COLOR)
        # - super basic draw
        # pl_obj = next(self.entities.get_by_class(Player))
        # pyv.pygame.draw.circle(self.screen, 'red', (pl_obj.x, pl_obj.y), 8)

        # - evo draw
        self._draw_player()

        # for visible_entity in self.entities.get_by_class(Table, Score, Ball, Racket, Spark):
        #    self.screen.blit(visible_entity.sprite.image, (visible_entity.x, visible_entity.y))
