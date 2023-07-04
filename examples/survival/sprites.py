from itertools import chain
from random import uniform, choice, randint, random

import pyved_engine as pyv
from z_constants import *


pg = pyv.pygame
vec = pg.math.Vector2
EngineEvTypes = pyv.EngineEvTypes
tilemap = pyv.tmx.get_ztilemap_module()
collide_hit_rect = tilemap.collide_hit_rect


# --- from pyTweening ---
def pt_checkRange(n):
    """Raises ValueError if the argument is not between 0.0 and 1.0.
    """
    if not 0.0 <= n <= 1.0:
        raise ValueError('Argument must be between 0.0 and 1.0.')


def easeInBack(n, s=1.70158):
    """A tween function that backs up first at the start and then goes to the destination.
    Args:
      n (float): The time progress, starting at 0.0 and ending at 1.0.
    Returns:
      (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().
    """
    pt_checkRange(n)
    return n * n * ((s + 1) * n - s)


def collided_with_wall(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        # Stick to wall if we hit it
        # Generally bad practice to use list[0] but this works for now
        # with the yellow square we based on corner of rect, for sprite use center.
        if hits:
            if hits[0].rect.centerx >= sprite.hit_rect.centerx:  # sprite.x starts at top left of sprite
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            elif hits[0].rect.centerx <= sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        # Stick to wall if we hit it
        # Generally bad practice to use list[0] but this works for now
        if hits:
            if hits[0].rect.centery >= sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            elif hits[0].rect.centery <= sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y, stats=None):
        self.wanna_exit = False
        self.msg_emitter = pyv.Emitter()

        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        # self.image = pg.Surface((TILESIZE, TILESIZE))
        # self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        # x and y determine where the plyr will be drawn. See update()
        # self.x = x * TILESIZE
        # self.y = y * TILESIZE
        # self.vx, self.vy = 0, 0
        self.pos = vec(x, y)  # * TILESIZE
        self.vel = vec(0, 0)
        self.rot = 270  # rotation
        self.last_shot = 0
        self.health = PLAYER_MAX_HEALTH
        self.is_damaged = False
        self.comms = 0
        self.weapon_selection = 0
        self.weapons = ['pistol']
        self.ammo = {
            'pistol_ammo': 0,
            'shotgun_ammo': 0,
            'uzi_ammo': 0,
            'landmines': 0
        }
        if stats:
            self.stats = stats
        else:
            self.stats = {
                'accuracy_bonus': 0,
                'fire_rate_bonus': 0,
                'ammo_bonus': 0,
                'dmg_bonus': 0,
                'speed_bonus': 0,
                'bonuses': 0
            }
        self.curr_weapon = self.weapons[self.weapon_selection]

    def got_hit(self):
        self.is_damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 4)

    def get_keys(self):
        self.rot_speed = 0
        # self.vx, self.vy = 0, 0
        self.vel = vec(0, 0)

        keys = pg.key.get_pressed()
        pg.key.set_repeat()
        # Keeping this here for pre-rotate movement reference:
        # if self.vel.x != 0 and self.vel.y != 0:
        # self.vel *= 0.7071
        # self.vx *= 0.7071  # 1 / Sqrt of 2
        # self.vy *= 0.7071
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED + self.stats['speed_bonus'], 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            self.shoot()
        if keys[pg.K_ESCAPE]:
            self.wanna_exit = True
            self.msg_emitter.pev(
                EngineEvTypes.Gameover
            )
            print('emit gameover Msg!')

    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        # rotate the image using the above calculation
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        if self.is_damaged:
            try:
                # Use white/transparency to show damage effect. Experiment w special flags if you want.
                self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.is_damaged = False
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        # Rotate around the center of the rect for smooth rot animation
        self.hit_rect.centerx = self.pos.x  # self.x
        collided_with_wall(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collided_with_wall(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

    def shoot(self):
        now = pg.time.get_ticks()
        curr_weapon = WEAPONS[self.curr_weapon]
        bullet_usage = curr_weapon['bullet_usage']
        curr_ammo = self.get_ammo(curr_weapon)
        if self.game.weapon_sounds:
            snd = choice(self.game.weapon_sounds[self.curr_weapon])
        else:
            snd = None

        if now - self.last_shot > curr_weapon['fire_rate'] - self.stats['fire_rate_bonus']:
            if curr_ammo >= bullet_usage:
                if snd:
                    snd.play()
                self.last_shot = now
                dir = vec(1, 0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                self.vel -= vec(curr_weapon['kickback'], 0).rotate(-self.rot)
                MuzzleFlash(self.game, pos)
                self.reduce_ammo(curr_weapon)
                for i in range(curr_weapon['bullet_count']):
                    spread = uniform(min(-curr_weapon['bullet_spread'] + self.stats['accuracy_bonus'], 0),
                                     curr_weapon['bullet_spread'])
                    Bullet(self.game, pos, dir.rotate(spread), curr_weapon['damage'] + self.stats['dmg_bonus'])
            else:
                self.last_shot = now
                if snd:
                    snd = self.game.weapon_sounds['empty'][0]
                    snd.play()

        # Interesting code to synchronize sounds, may use it.
        if snd:
            if snd.get_num_channels() > 2:
                snd.stop()

    def change_weapon(self):
        self.weapon_selection += 1
        if self.weapon_selection >= len(self.weapons):
            self.weapon_selection = 0
        self.curr_weapon = self.weapons[self.weapon_selection]

    def get_ammo(self, weapon):
        curr_weapon = self.curr_weapon
        if curr_weapon == 'pistol':
            return self.ammo['pistol_ammo']
        elif curr_weapon == 'shotgun':
            return self.ammo['shotgun_ammo']
        elif curr_weapon == 'uzi':
            return self.ammo['uzi_ammo']

    def reduce_ammo(self, weapon):
        curr_weapon = self.curr_weapon
        if curr_weapon == 'pistol':
            self.ammo['pistol_ammo'] -= 1
        elif curr_weapon == 'shotgun':
            self.ammo['shotgun_ammo'] -= 1
        elif curr_weapon == 'uzi':
            self.ammo['uzi_ammo'] -= 1

    def place_mine(self):
        if self.ammo['landmines'] >= 1:
            # spawn mine in front of player. Not under.
            pos = self.pos + vec(40, 0).rotate(-self.rot)
            Landmine(self.game, pos, LANDMINE_DAMAGE + self.stats['dmg_bonus'])
            self.ammo['landmines'] -= 1
            # has sound
            if self.game.effects_sounds:
                self.game.effects_sounds['place_mine1'].play()


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img.copy()  # prevent bugs. E.g. duplicate health bars
        self.rect = self.image.get_rect()  # fixed bug by using mob_hit_rect.copy() where mobs disappear
        self.rect.x = x
        self.rect.y = y
        self.hit_rect = MOB_HIT_RECT.copy()
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.hit_rect.center = self.rect.center  # Trying to fix a bug
        self.rot = 0
        self.max_health = 50
        self.health = 50
        self.speed = choice(MOB_SPEEDS)
        self.target = self.game.player
        self.is_chasing = False
        self.avoid_rad = MOB_AVOID_RADIUS

    def draw_health(self):
        hp_percent = self.health / self.max_health
        if hp_percent > .65:
            col = GREEN
        elif hp_percent > .45:
            col = YELLOW
        else:
            col = RED
        bar_width = int(self.rect.width * self.health / 100)
        bar_height = 7
        self.health_bar = pg.Rect(0, 0, bar_width, bar_height)
        if self.health < self.max_health:
            pg.draw.rect(self.image, col, self.health_bar)

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                # calculate distance between self's vector and other mobs' vec
                dist = self.pos - mob.pos
                if 0 < dist.length() < self.avoid_rad:
                    # normalize() returns a vector with same dir but length 1
                    self.acc += dist.normalize()  # TODO: learn how vectors work

    def rotate(self):
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)

    def update(self):
        if self.health <= 0:
            # sound
            if self.game.zombie_death_sounds:
                choice(self.game.zombie_death_sounds).play()
            self.kill()
            if len(self.game.splat_images):  # blood active
                splat_img = choice(self.game.splat_images)
                self.game.map_img.blit(splat_img, self.pos - vec(32, 32))
            # pg.display.flip()

        else:
            self.rotate()

            # detection starts --
            # See notes below to know why we use: ** 2
            # Also, alert mob if shot was fired near it
            target_dist = self.target.pos - self.pos
            if not self.is_chasing:
                if target_dist.length_squared() < MOB_DETECT_RADIUS ** 2:
                    self.is_chasing = True
            """
            Technically, the line below works. But length() of a vector is calculated with Bob's theorem.
            This means getting the square root, which is an expensive operation. sqrt(x**2 + y**2) We save time
            by comparing the squared values instead
            """
            # if target_dist.length() < MOB_DETECT_RADIUS:
            # -- detection done

            if self.is_chasing:
                if self.game.zombie_moan_sounds:  # have sound
                    if random() < 0.002:
                        choice(self.game.zombie_moan_sounds).play()
                print('--------chasing zombie update----------')
                print('dt= ', self.game.dt)
                print('pos= ', self.pos)
                interm =(self.game.player.pos - self.pos)
                print('interm: ',  interm)
                self.rot = interm.angle_to(vec(1, 0))
                print('rot= ',  self.rot)
                self.rect = self.image.get_rect()
                self.rect.center = self.pos

                self.acc = vec(1, 0).rotate(-self.rot)

                # temp disabled to see if bug comes from here
                # self.avoid_mobs()
                print('(-)acc= ', self.acc)
                self.acc.scale_to_length(self.speed)

                self.acc += self.vel * -1.3  # friction to slow down movement
                print('(+)acc= ', self.acc)
                self.vel += self.acc * self.game.dt

                print('vel= ', self.vel)

                # Using equation of motion
                self.pos += self.vel * self.game.dt + (0.5 * self.acc * (self.game.dt ** 2))
                self.hit_rect.centerx = self.pos.x
                collided_with_wall(self, self.game.walls, 'x')
                self.hit_rect.centery = self.pos.y
                collided_with_wall(self, self.game.walls, 'y')
                self.rect.center = self.hit_rect.center

            if self.health < self.max_health:
                self.draw_health()


class Runner(Mob):
    def __init__(self, game, x, y):
        Mob.__init__(self, game, x, y)
        self.image = self.game.runner_img
        self.hit_rect = RUNNER_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.speed = choice(RUNNER_SPEEDS)
        self.avoid_rad = RUNNER_AVOID_RADIUS

    def rotate(self):
        self.image = pg.transform.rotate(self.game.runner_img, self.rot)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.weapon = WEAPONS[game.player.curr_weapon]
        self.image = game.bullet_images[game.player.curr_weapon]  # game.pistol_bullet_img
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)  # create new vector so we're not referencing the player's pos directly
        self.rect.center = self.pos
        # spread = uniform(-BULLET_SPREAD, BULLET_SPREAD)
        self.vel = dir * self.weapon['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.targets = self.game.mobs
        self.damage = damage
        # My solution: Use a Surface instead of the difficult image.

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.curr_weapon]['bullet_lifetime']:
            self.kill()
        self.alert_mobs()

    def alert_mobs(self):
        for target in self.targets:
            if not target.is_chasing:
                target_dist = target.pos - self.pos
                if target_dist.length_squared() < MOB_DETECT_RADIUS ** 2:
                    target.is_chasing = True


class Landmine(pg.sprite.Sprite):
    def __init__(self, game, pos, damage):
        self._layer = ITEMS_LAYER  # May change
        self.groups = game.all_sprites, game.landmines
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images['placed_mine']
        self.image = pg.transform.scale(self.image, (36, 36))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)  # create new vector so we're not referencing the player's pos directly
        self.rect.center = self.pos
        self.targets = self.game.mobs
        self.damage = damage
        self.last_update = pg.time.get_ticks()
        self.beep_count = 3

    def update(self):
        now = pg.time.get_ticks()
        if self.beep_count > 0 and now - self.last_update > 250:
            self.last_update = now
            if self.game.effects_sounds:
                self.game.effects_sounds['place_mine2'].play()
            self.beep_count -= 1


class Explosion(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites, game.explosions
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.pos = pos
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()
        # self.spawn_time = pg.time.get_ticks()
        self.image = game.explosion_frames[0]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.rect.center = pos

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 15:
            self.last_update = now
            self.image = self.game.explosion_frames[(self.current_frame + 1)]
            self.rect = self.image.get_rect()
            self.hit_rect = self.rect
            self.rect.center = self.pos
            self.current_frame += 1
            if self.current_frame >= len(self.game.explosion_frames) - 1:
                self.kill()


class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20, 30)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self._layer = WALL_LAYER
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, item_type, ratio):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.ratio = ratio

        #if item_type:
        self.ogImage = pg.transform.scale(game.item_images[item_type], ratio)
        if item_type not in GUN_IMAGES:
            self.ogImage.set_colorkey(BLACK)
        self.image = self.ogImage.copy()
        self.rect = self.image.get_rect()
        self.type = item_type
        self.rect.center = pos

        self.pos = pos

        self.item_alpha = chain(ITEM_ALPHA * 4)
        self.counter = ITEM_FADE_MIN
        self.increment = 3
        self.visible = True
        self.time_picked_up = 0

    def update(self):
        self.visible = True
        return
        # Fade in/out animation --> see game#draw
        if self.visible:
            self.image = self.ogImage.copy()
            self.counter += self.increment
            if self.counter > ITEM_FADE_MAX or self.counter < ITEM_FADE_MIN:
                self.increment = -self.increment
            self.image.fill((255, 255, 255, min(255, self.counter)), special_flags=pg.BLEND_RGBA_MULT)
            self.rect.center = self.pos
        else:
            now = pg.time.get_ticks()
            if now - self.time_picked_up > 60000:
                self.visible = True

    def make_invisible(self):
        self.visible = False
        self.time_picked_up = pg.time.get_ticks()
        self.image = pg.Surface(self.ratio).convert_alpha()
        self.image.set_colorkey(BLACK)


class BonusItem(Item):
    def __init__(self, game, pos, axis, ratio):
        # super().__init__(game, pos, None, ratio)

        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.transform.scale(game.item_images['bonus'], ratio)
        # self.image = self.ogImage.copy()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos = pos
        # self.animate = None
        self.animate = easeInBack  # TODO: Look up function to see what included arg can do
        self.step = 0  # Value btwn 0 and 1, used to step thru animation
        self.dir = 1  # Will be btwn 1 and -1. E.g. To bob up and down / side to side
        self.type = axis

    def update(self):
        # Bobbing animation
        offset = ITEM_BOB_RANGE * (self.animate(self.step / ITEM_BOB_RANGE) - 0.5)  # - 0.5 to start 'mid-animation'
        if self.type == 'y':
            self.rect.centery = self.pos.y + offset * self.dir
        else:
            self.rect.centerx = self.pos.x + offset * self.dir
        self.step += ITEM_BOB_SPEED
        if self.step > ITEM_BOB_RANGE:
            self.step = 0  # Restart/reposition
            self.dir *= -1  # allows us to switch btwn up and down

    def activate(self, plyr):
        txt = ""
        if plyr.stats['bonuses'] % 3 == 0:
            plyr.stats['speed_bonus'] += 10
            txt = "SPEED BONUS!"
        elif plyr.stats['bonuses'] % 2 == 0:
            plyr.stats['dmg_bonus'] += 3
            txt = "DAMAGE BONUS!"
        else:
            plyr.stats['ammo_bonus'] += 3
            txt = "AMMO PICKUP BONUS!"
        Text(self.game, self.pos.x, self.pos.y, txt, 24)


class Tower(Obstacle):
    def __init__(self, game, x, y, w, h):
        Obstacle.__init__(self, game, x, y, w, h)
        self.groups = game.all_sprites, game.towers, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.transform.scale(game.item_images['tower'], (int(w), int(h)))


class Text(pg.sprite.Sprite):
    def __init__(self, game, x, y, text, font_size=32):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = x
        self.y = y
        self.text = text
        font = pg.font.Font(self.game.title_font, font_size)  # font_name, size
        self.image = font.render(text, True, BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Fade(pg.sprite.Sprite):
    def __init__(self, direction):
        super().__init__()
        self.rect = pg.display.get_surface().get_rect()
        self.image = pg.Surface(self.rect.size, flags=pg.SRCALPHA)
        self.direction = direction
        # self.alpha = 0 if direction > 0 else self.alpha = 255

    def update(self):
        if self.direction > 0:
            self.image.fill(0, 0, 0, self.alpha)
        elif self.direction < 0:
            self.image.fill(255, 255, 255, self.alpha)
        self.alpha += self.direction
        if self.alpha > 255 or self.alpha < 0:
            self.kill()


class Spritesheet:
    # Utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.set_colorkey(BLACK)
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 1, height // 1))  # // --> force to int
        return image
