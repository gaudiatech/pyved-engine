import pygame

import katagames_engine as pyv
from en_entities import Player


# SysInit(entities),
# SysControl(entities, pygame.event.get),
# SysMovement(entities),
# SysRoundStarter(entities, clock),
# SysGoal(entities),
# SysDraw(entities, screen),


class SysInput(pyv.System):
    def __init__(self, entities):
        self.gameover = False
        self.entities = entities

    def proc(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.gameover = True

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.gameover = True
                elif ev.key == pygame.K_UP:
                    pl_obj = next(self.entities.get_by_class(Player))
                    pl_obj.vy = -1.845
                elif ev.key == pygame.K_DOWN:
                    pl_obj = next(self.entities.get_by_class(Player))
                    pl_obj.vy = +1.744

            elif ev.type == pygame.KEYUP:
                tmp = pygame.key.get_pressed()
                if not tmp[pygame.K_DOWN] and not tmp[pygame.K_UP]:
                    pl_obj = next(self.entities.get_by_class(Player))
                    pl_obj.vy = 0


class SysEntityMover(pyv.System):
    def __init__(self, ent):
        self.entities = ent

    def proc(self):
        pl_obj = next(self.entities.get_by_class(Player))
        if pl_obj.vx != 0.0:
            pl_obj.x += pl_obj.vx
        if pl_obj.vy != 0.0:
            pl_obj.y += pl_obj.vy


class SysGraphicalRepr(pyv.System):
    def __init__(self, entities, screen):
        self.entities = entities
        self.screen = screen

    def proc(self):
        self.screen.fill('antiquewhite2')
        pl_obj = next(self.entities.get_by_class(Player))
        pygame.draw.circle(self.screen, 'red', (pl_obj.x, pl_obj.y), 8)
        # for visible_entity in self.entities.get_by_class(Table, Score, Ball, Racket, Spark):
        #    self.screen.blit(visible_entity.sprite.image, (visible_entity.x, visible_entity.y))
