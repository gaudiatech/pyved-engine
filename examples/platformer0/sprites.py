import pyved_engine as pyv
from pyved_engine import *


Spr = pyv.pygame.sprite.Sprite


class Enemy(Spr):

    def __init__(self, location, *groups):
        super(Enemy, self).__init__(*groups)
        self.image = pyv.vars.images['enemy']
        self.rect = pyv.pygame.rect.Rect(location, self.image.get_size())
        self.direction = 1

    def update(self, dt, game):
        self.rect.x += self.direction * 100 * dt
        for cell in game.tilemap.layers['triggers'].collide(self.rect, 'reverse'):
            if self.direction > 0:
                self.rect.right = cell.left
            else:
                self.rect.left = cell.right
            self.direction *= -1
            break
        if self.rect.colliderect(game.player.rect):
            game.player.is_dead = True


class Missile(Spr):
    speed = 233

    def __init__(self, location, direction, *groups):
        super(Missile, self).__init__(*groups)
        self.image = pyv.vars.images['missile']
        self.rect = pyv.pygame.rect.Rect(location, self.image.get_size())
        self.direction = direction
        self.lifespan = 0.8

    def update(self, dt, game):
        self.lifespan -= dt
        if self.lifespan < 0:
            self.kill()
            return
        self.rect.x += self.direction * self.speed * dt

        if pyv.pygame.sprite.spritecollide(self, game.enemies, True):
            self.kill()


class Player(Spr):
    def __init__(self, location, *groups):
        super(Player, self).__init__(*groups)

        self.right_image = pyv.vars.images['player-right']
        self.left_image = pyv.vars.images['player-left']
        self.image = self.right_image

        self.rect = pyv.pygame.rect.Rect(location, self.image.get_size())
        self.resting = False
        self.dy = 0
        self.is_dead = False
        self.direction = 1
        self.gun_cooldown = 0

    def update(self, dt, game):  # joueur recoit reference sur game
        last = self.rect.copy()

        key = pyv.get_pressed_keys()  # joueur controle sa position lui mm. Si implem joystick -> ds le cul lulu
        if key[K_LEFT]:
            self.rect.x -= 300 * dt
            self.image = self.left_image
            self.direction = -1
        if key[K_RIGHT]:
            self.rect.x += 300 * dt
            self.image = self.right_image
            self.direction = 1

        if key[K_LCTRL] and not self.gun_cooldown:
            if self.direction > 0:
                Missile(self.rect.midright, 1, game.sprites)
            else:
                Missile(self.rect.midleft, -1, game.sprites)
            self.gun_cooldown = 1

        self.gun_cooldown = max(0, self.gun_cooldown - dt)

        if self.resting and key[K_SPACE]:
            self.dy = -500
        self.dy = min(400, self.dy + 40)

        self.rect.y += self.dy * dt

        new = self.rect
        self.resting = False

        for cell in game.tilemap.layers['triggers'].collide(new, 'blockers'):
            blockers = cell['blockers']
            if 'l' in blockers and last.right <= cell.left < new.right:
                new.right = cell.left
            if 'r' in blockers and last.left >= cell.right > new.left:
                new.left = cell.right
            if 't' in blockers and last.bottom <= cell.top < new.bottom:
                self.resting = True
                new.bottom = cell.top
                self.dy = 0
            if 'b' in blockers and last.top >= cell.bottom > new.top:
                new.top = cell.bottom
                self.dy = 0

        # game.tilemap fait office de vue, player obj y fait ref directementr
        # game.tilemap.set_focus(new.x, new.y)
        # - nouvelle separation
        game.viewport.set_focus(new.x, new.y)
