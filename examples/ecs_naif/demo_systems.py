import math

import pyved_engine as pyv
from demo_entities import Player


class SysInput(pyv.System):
    def __init__(self, entities):
        self.gameover = False
        self.entities = entities

    def proc(self):
        pygame = pyv.pygame
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.gameover = True

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.gameover = True
                else:
                    pl_obj = next(self.entities.get_by_class(Player))
                    if ev.key == pygame.K_UP:
                        pl_obj = next(self.entities.get_by_class(Player))
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
            xcap, ycap = pyv.config.SCR_SIZE
            if pl_obj.x < 0:
                pl_obj.x += xcap
            elif pl_obj.x >= xcap:
                pl_obj.x -= xcap

            if pl_obj.y < 0:
                pl_obj.y += ycap
            elif pl_obj.y >= ycap:
                pl_obj.y -= ycap


class SysView2D(pyv.System):
    SHIP_COLOR = '#22feb4'
    RAD = 17

    def __init__(self, entities, screen):
        self.entities = entities
        self.screen = screen

    def _draw_player(self):
        surf = self.screen
        pmath = pyv.pygame.math

        # fetch player pos & orientation
        pl_obj = next(self.entities.get_by_class(Player))
        pt_central = (pl_obj.x, pl_obj.y)
        orientation = pl_obj.angle

        tv = [
            pmath.Vector2(),
            pmath.Vector2(),
            pmath.Vector2()
        ]
        tv[0].from_polar((self.RAD * 1.25, math.degrees(orientation + (2.0 * math.pi / 3))))
        tv[1].from_polar((self.RAD * 3, math.degrees(orientation)))
        tv[2].from_polar((self.RAD * 1.25, math.degrees(orientation - (2.0 * math.pi / 3))))
        pt_li = [
            pmath.Vector2(*pt_central),
            pmath.Vector2(*pt_central),
            pmath.Vector2(*pt_central)
        ]
        for i in range(3):
            pt_li[i] += tv[i]
        pyv.pygame.draw.polygon(surf, self.SHIP_COLOR, pt_li, 2)

    def proc(self):
        self.screen.fill('darkblue')
        # - super basic draw
        # pl_obj = next(self.entities.get_by_class(Player))
        # pyv.pygame.draw.circle(self.screen, 'red', (pl_obj.x, pl_obj.y), 8)

        # - evo draw
        self._draw_player()

        # for visible_entity in self.entities.get_by_class(Table, Score, Ball, Racket, Spark):
        #    self.screen.blit(visible_entity.sprite.image, (visible_entity.x, visible_entity.y))
