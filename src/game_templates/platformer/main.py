"""
this demo is a collab.
OPEN-SOURCE, public domain

created by (reverse chronological order)
 -wkta-tom
 -Renfred Harper
 -Richard Jones (author of the first prototype, incl. xml parsing)

My goal here in 2022:
to provide a platformer game template for kengi, refe to:
github.com/gaudiatech/kengi so every game dev can learn more,
discover cool stuff that saves time if youre already a pygame user.
"""


import katagames_engine as kengi

pygame = kengi.pygame
Spr = pygame.sprite.Sprite


def ld_asset(name):
    return pygame.image.load('assets/' + name)


class Enemy(Spr):
    image = ld_asset('enemy.png')

    def __init__(self, location, *groups):
        super(Enemy, self).__init__(*groups)
        self.rect = pygame.rect.Rect(location, self.image.get_size())
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
    image = ld_asset('missile.png')
    speed = 233

    def __init__(self, location, direction, *groups):
        super(Missile, self).__init__(*groups)
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.direction = direction
        self.lifespan = 0.8

    def update(self, dt, game):
        self.lifespan -= dt
        if self.lifespan < 0:
            self.kill()
            return
        self.rect.x += self.direction * self.speed * dt

        if pygame.sprite.spritecollide(self, game.enemies, True):
            self.kill()


class Player(Spr):
    def __init__(self, location, *groups):
        super(Player, self).__init__(*groups)

        self.right_image = ld_asset('player-right.png')
        self.left_image = ld_asset('player-left.png')
        self.image = self.right_image

        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.resting = False
        self.dy = 0
        self.is_dead = False
        self.direction = 1
        self.gun_cooldown = 0

    def update(self, dt, game):  # joueur recoit reference sur game
        last = self.rect.copy()

        key = pygame.key.get_pressed()  # joueur controle sa position lui mm. Si implem joystick -> ds le cul lulu
        if key[pygame.K_LEFT]:
            self.rect.x -= 300 * dt
            self.image = self.left_image
            self.direction = -1
        if key[pygame.K_RIGHT]:
            self.rect.x += 300 * dt
            self.image = self.right_image
            self.direction = 1

        if key[pygame.K_LCTRL] and not self.gun_cooldown:
            if self.direction > 0:
                Missile(self.rect.midright, 1, game.sprites)
            else:
                Missile(self.rect.midleft, -1, game.sprites)
            self.gun_cooldown = 1

        self.gun_cooldown = max(0, self.gun_cooldown - dt)

        if self.resting and key[pygame.K_SPACE]:
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


class MyGame:

    def launch(self):
        print('--------- controls ----------')
        print('left/right arrows to move |  Left Ctrl key to shoot | Spacebar to jump')
        print()
        self.wanna_quit = False

        kengi.core.init('old_school')
        self.clock = pygame.time.Clock()
        self.scr = kengi.core.get_screen()
        scr_size = self.scr.get_size()

        self.tilemap = kengi.tmx.data.load_tmx('level.tmx')  # -> Tilemap instance

        # - search for background
        if self.tilemap.background:
            print('info about bg found in .tmx file, ok!')
            # turn background image to a sprite, so we can repeat it easily
            bg = pygame.sprite.Sprite()
            bg.image = pygame.image.load(self.tilemap.background['img_path'])
            bg.rect = bg.image.get_rect()
            bg.rect.left = -16 + self.tilemap.background['offsetx']
            bg.rect.top = 0
            print(bg.rect.topleft)
            self.bg = bg
        else:
            self.bg = None

        self.viewport = kengi.tmx.misc.Viewport(self.tilemap, (0,0), scr_size)
        self.first_run = True

        self._reset_game()
        while not self.wanna_quit:
            self._do_run()
            self._reset_game()

        # quit
        kengi.core.cleanup()

    def _reset_game(self):
        # TODO improve design
        if not self.first_run:  # how to write this better?
            self.tilemap.layers.pop()
            self.tilemap.layers.pop()

        self.sprites = kengi.tmx.misc.SpriteLayer()
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        print(start_cell)

        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        self.tilemap.layers.append(self.sprites)
        self.enemies = kengi.tmx.misc.SpriteLayer()

        for enemy in self.tilemap.layers['triggers'].find('enemy'):
            Enemy((enemy.px, enemy.py), self.enemies)
        self.tilemap.layers.append(self.enemies)

    def _do_run(self):
        self.first_run = False
        gameover = False

        while not gameover:
            dt = self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameover = True
                    self.wanna_quit =True
                    break
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    gameover = True
                    self.wanna_quit = True
                    break

            # logic update
            if self.player.is_dead:
                gameover = True
                print(' ** you die! **')
            else:
                self.tilemap.update(dt / 1000., self)

            # - display
            self.scr.blit(self.bg.image, (0, 0))
            self.viewport.draw(self.scr)
            kengi.core.display_update()


if __name__ == '__main__':
    g = MyGame()
    g.launch()
    del g
