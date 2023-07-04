import time
from random import random, choice

import pyved_engine as katasdk

katasdk.bootstrap_e()
pygame = katasdk.pygame

from sprites import Explosion, Obstacle, Player, Tower, BonusItem, Runner, Mob, Item

# TODO if you wanna fix bugs, the most important is :
#  - to fix the sound: use a sound controller + use several channels in local ctx
#  - find why icons are blinking and remove this effect
# --- constants
NO_SOUND = False
NO_FOG = True
SNDPATH = 'assets/snd/'

# ---
WEBCTX = False  # katasdk.runs_in_web()


def cload_img(source):
    global WEBCTX
    if not WEBCTX:
        s = 'assets/' + source
    else:
        s = source
    return pygame.image.load(s)


# >>>const.py
# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

FONT_NAME = 'arial'

# game settings
# Ensure no partial squares with these values
# old
# WINDOW_WIDTH = 1024  # 16 * 64 or 32 * 32 or 64 * 16
WINDOW_WIDTH = 832  # 13x64
# old
# WINDOW_HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
WINDOW_HEIGHT = 704  # 11x64

FPS = 60
TITLE = "Zombie Top-down Shooter"
BGCOLOR = LIGHTGREY

# Usu. in pows of 2 e.g. 8, 16, 32, 64, etc.
TILESIZE = 64
GRIDWIDTH = WINDOW_WIDTH / TILESIZE
GRIDHEIGHT = WINDOW_HEIGHT / TILESIZE

WALL_IMG = 'tile_179.png'

# Player settings
PLAYER_MAX_HEALTH = 100
PLAYER_SPEED = 250
PLAYER_ROT_SPEED = 250  # degrees per second
PLAYER1_IMG = 'manBlue_gun.png'
PLAYER2_IMG = '(zombie)hitman_gun.png'
PLAYER_HIT_RECT = katasdk.pygame.Rect(0, 0, 35, 35)  # needs to be Rect to get center (not Surface)
# By default, player facing right, so offset the bullet 30 to the right (x) and 10 down (y)
BARREL_OFFSET = katasdk.pygame.math.Vector2(30, 10)
PLAYER_HEALTH_BAR_HEIGHT = 20
PLAYER_HEALTH_BAR_WIDTH = 100

# Weapon settings
# BULLET_IMG = 'bullet.png' # Using Surface instead.
# MAYBE: Create a Weapon class instead of dictionaries in our settings file
WEAPONS = {}
WEAPONS['pistol'] = {
    'bullet_speed': 750,
    'bullet_lifetime': 1250,
    'fire_rate': 425,
    'kickback': 200,
    'bullet_spread': 6,
    'damage': 10,
    'bullet_count': 1,
    'bullet_usage': 1

}
WEAPONS['shotgun'] = {
    'bullet_speed': 500,
    'bullet_lifetime': 500,
    'fire_rate': 1000,
    'kickback': 500,
    'bullet_spread': 24,
    'damage': 8,
    'bullet_count': 5,
    'bullet_usage': 1
}
WEAPONS['uzi'] = {
    'bullet_speed': 1000,
    'bullet_lifetime': 750,
    'fire_rate': 175,
    'kickback': 300,
    'bullet_spread': 15,
    'damage': 7,
    'bullet_count': 1,
    'bullet_usage': 1
}

LANDMINE_DAMAGE = 35
LANDMINE_KNOCKBACK = 50

# Mob settings
MOB_IMG = 'zombie1_hold.png'
MOB_SPEEDS = [220, 240, 260]
MOB_HIT_RECT = pygame.Rect(0, 0, 30, 30)
MOB_DAMAGE = 10
MOB_KNOCKBACK = 25
MOB_AVOID_RADIUS = 70  # in px
MOB_DETECT_RADIUS = 325

# Runner settings
RUNNER_IMG = 'zombie2_hold.png'
RUNNER_SPEEDS = [350, 365]
RUNNER_HIT_RECT = pygame.Rect(0, 0, 30, 30)
RUNNER_DAMAGE = 15
RUNNER_KNOCKBACK = 30
RUNNER_AVOID_RADIUS = 45  # in px
RUNNER_DETECT_RADIUS = 350

# Items
ITEM_IMAGES = {
    "health": "(zombie)health_icon.png",
    "pistol_ammo": "(zombie)pistol_ammo.png",
    "shotgun_ammo": "(zombie)shotgun_ammo.png",
    "uzi_ammo": "(zombie)uzi_ammo.png",
    "landmine": "(zombie)mine_icon.png",
    "bonus": "(zombie)bonus.png",
    "comms": "(zombie)comms_icon.png",
    "shotgun": "(zombie)shotgun.png",
    "pistol": "(zombie)pistol.png",
    "uzi": "(zombie)uzi.png",
    "placed_mine": "(zombie)landmine.png",
    "tower": "(zombie)cell_tower.png"
}

GUN_IMAGES = {
    "pistol": "(zombie)pistol.png",
    "shotgun": "(zombie)shotgun.png",
    "uzi": "(zombie)uzi.png"
}

# Item effectiveness
HEALTH_PICKUP_AMT = 25
PISTOL_AMMO_PICKUP_AMT = 6
SHOTGUN_AMMO_PICKUP_AMT = 6
UZI_AMMO_PICKUP_AMT = 14

# Effects
MUZZLE_FLASHES = ["(zombies)whitePuff15.png", "(zombies)whitePuff16.png", "(zombies)whitePuff17.png",
                  "(zombies)whitePuff18.png"]
FLASH_DURATION = 40  # ms
SPLAT_IMAGES = ['blood-splatter1.png', 'blood-splatter3.png', 'blood-splatter4.png']

ITEM_BOB_RANGE = 50
ITEM_BOB_SPEED = 3

DAMAGE_ALPHA = [i for i in range(0, 255, 20)]
ITEM_ALPHA = [i for i in range(0, 255, 2)]
ITEM_FADE_MIN = 50
ITEM_FADE_MAX = 245
NIGHT_COLOR = (133, 133, 180)
LIGHT_RADIUS = (350, 350)
LIGHT_MASK = '(zombie)light_350_med.png'

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1

# Sounds
BG_MUSIC = 'Disturbed-Soundscape.ogg'
MENU_MUSIC = 'espionage.ogg'
LVL1_MUSIC = 'City-of-the-Disturbed.ogg'
ZOMBIE_MOAN_SOUNDS = [
    'brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
    'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav'
]
# for k in range(len(ZOMBIE_MOAN_SOUNDS)):
#     ZOMBIE_MOAN_SOUNDS[k] = ZOMBIE_MOAN_SOUNDS[k]

ZOMBIE_DEATH_SOUNDS = ['splat-15.wav']
PLAYER_HIT_SOUNDS = ['8.wav', '9.wav', '10.wav', '11.wav']
WEAPON_SOUNDS = {
    'pistol': ['pistol.wav'],
    'shotgun': ['shotgun.wav'],
    'uzi': ['uzi.wav'],
    'empty': ['empty_gun.wav']
}
# for k, v in WEAPON_SOUNDS.items():
#     WEAPON_SOUNDS[k] = ['assets/' + v[0], ]

EFFECTS_SOUNDS = {
    'level_start': 'level_start.wav',
    'health_up': 'item_pickup.ogg',
    'item_pickup': 'item_pickup.ogg',
    'ammo_pickup': 'ammo_pickup.ogg',
    'gun_pickup': 'gun_pickup.wav',
    'explosion': 'short_explosion.ogg',
    'place_mine1': 'drop_sound.wav',
    'place_mine2': '1beep.mp3'
}
# for k, v in EFFECTS_SOUNDS.items():
#     EFFECTS_SOUNDS[k] = 'assets/' + v
# -------------


STORIES = {
    'tutorial': ["Been a while since I came out of hiding.",
                 "Supplies are running low and I don't know how much longer "
                 "things can last.", "There's a tower here I can use to communicate with other survivors.",
                 "I just need to find the device for communication.", "Well... won't do any good to just sit here.",
                 "I need to find that comms device... I pray that I can get back to the tower alive."],

    'level1': ["Received a distress call.", "Didn't come with much info. Likely a lone survivor.", "Probably"
                                                                                                   " won't survive.",
               "Still, it's a good excuse to clear the local area of zombies.",
               "Been waiting to bring out the big guns.", "Time to go to work >"],

    'ending': ["THANKS FOR PLAYING!", "IF YOU ENJOYED THIS EXPERIENCE AND WANT ME TO BUILD", "THE REST OF THE GAME,",
               "LET ME KNOW IN THE COMMENTS!", "YOU CAN QUIT THE GAME NOW OR PRESS THE ENTER KEY",
               "TO RETURN TO THE MAIN MENU."]
}

LEVELS = {
    'tutorial.tmx': {
        'objective': 'return_comms',
        'plyr': PLAYER1_IMG,
        'story': STORIES['tutorial'],
        'music': BG_MUSIC
    },

    'level1.tmx': {
        'objective': 'kill_all_zombies',
        'plyr': PLAYER2_IMG,
        'story': STORIES['level1'],
        'music': LVL1_MUSIC
    },

    'level1-chris.tmx': {
        'objective': 'return_comms',
        'plyr': PLAYER1_IMG,
        'story': 'whatever!',
        'music': LVL1_MUSIC
    },

    'ending': {
        'story': STORIES['ending']
    }
}

# ----------- global vars
g = None
saved_t = None

import pyved_engine as pyv

tilemap = pyv.tmx.get_ztilemap_module()
collide_hit_rect = tilemap.collide_hit_rect
pg = pygame
vec = pg.math.Vector2
WARP_BACK_SIG = [2, 'niobepolis']
glclock = None
basefont = None  # will store a (pygame)font object


# >>>sprites.py
class IngameText(pg.sprite.Sprite):
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


class GameWorld:
    # todo separation M.V.C.

    def __init__(self):
        self.running = True
        self.game_over = False  # doublon?
        self.playing = True  # true when player selects 'new game' or 'continue'

        # attributs obligés
        self.screen = None  # init from outside
        self.camera = None
        self.all_sprites = None

        # a bit like constants / pre-init vars
        self.game_folder = 'assets'  # path.dirname(__file__)  # Where our game is running from
        # self.img_folder = path.join(self.game_folder, 'zassets')
        self.sound_folder = 'assets/'
        self.music_folder = 'assets/'

        self.map_folder = 'assets/maps'
        self.level_complete = False
        self.dt = 0  # mesure elapsed time between frames
        self.all_sounds = []
        self.soundfx_lvl = .6
        self.music_lvl = .8
        self.clock = pg.time.Clock()
        self.draw_debug = True

        self.paused = False

        # fonts
        self.title_font = self.menu_font = self.hud_font = None
        # self.title_font = path.join(self.img_folder, 'DemonSker-zyzD.ttf')  # TTF = True Type Font
        # self.menu_font = path.join(self.img_folder, 'DemonSker-zyzD.ttf')  # TODO: Experiment
        # self.hud_font = path.join(self.img_folder, 'DemonSker-zyzD.ttf')

        # gfx
        self.fog = None
        self.wall_img = None
        self.mob_img = None
        self.runner_img = None
        self.gun_images = None
        self.light_mask = None
        self.light_rect = None
        self.dim_screen = None

        # sfx
        self.effects_sounds = None
        self.weapon_sounds = None
        self.player_hit_sounds = None
        self.zombie_death_sounds = None
        self.zombie_moan_sounds = None

        # for LOAD_DATA
        self.explosion_sheet = None
        self.explosion_frames = None
        self.bullet_images = dict()
        self.pistol_bullet_img = None
        self.shotgun_bullet_img = None
        self.uzi_bullet_img = None
        self.gun_flashes = []
        self.item_images = {}
        self.splat_images = {}

        # for LOAD_LEVEL
        self.current_music = None
        self.player = None
        self.walls = self.towers = self.mobs = None
        self.bullets = self.items = self.landmines = self.explosions = None
        self.current_lvl = None  # Grab our game layout file (map)
        self.player_img = None
        self.objective = None
        self.story = None
        self.map = None
        self.map_img = None
        self.map_rect = None
        self.texts = None
        self.comms_req = None

        # related to ctrls
        # for weird reasons arrow keys are handled differentrly than other keys in events
        self.UP_KEY, \
            self.DOWN_KEY, \
            self.START_KEY, \
            self.BACK_KEY, \
            self.LEFT_KEY, \
            self.RIGHT_KEY = False, False, False, False, False, False

    def draw_text(self, text, font_name, size, color, x, y, align='nw'):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == 'nw':
            text_rect.topleft = (x, y)
        elif align == 'ne':
            text_rect.topright = (x, y)
        elif align == 'sw':
            text_rect.bottomleft = (x, y)
        elif align == 'se':
            text_rect.bottomright = (x, y)
        elif align == 'n':
            text_rect.midtop = (x, y)
        elif align == 'e':
            text_rect.midright = (x, y)
        elif align == 's':
            text_rect.midbottom = (x, y)
        elif align == 'w':
            text_rect.midleft = (x, y)
        elif align == 'center':
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        # Setting up explosion animation
        self.explosion_sheet = cload_img('(zombies)explosion.png')
        self.explosion_frames = []
        expl_width = 130
        expl_height = 130
        x = 0
        y = -25
        # Creating and iterating through each "square" of the explosion spritesheet
        # TODO better use a sprsheet 'cause this does not work in web ctx
        for i in range(5):
            for j in range(5):
                img = pg.Surface((expl_width, expl_height))
                img.blit(self.explosion_sheet, (0, 0), (x, y, expl_width, expl_height))
                img.set_colorkey(BLACK)
                img = pg.transform.scale(img, (round(expl_width * 2.8), round(expl_height * 2.8)))
                self.explosion_frames.append(img)
                x += expl_width
            x = 0
            y += expl_height

        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))  # BLACK with 180 transparency
        self.wall_img = cload_img('(zombies)tile_179.png').convert_alpha()  # Surface

        # TODO scaling?
        # self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))  # can scale image

        self.mob_img = cload_img('zombie1_hold.png').convert_alpha()  # Surface
        self.runner_img = cload_img(RUNNER_IMG).convert_alpha()
        # pg.draw.circle(surface, color, center, radius)  # Each image is a Surface
        self.gun_images = {}
        for gun in GUN_IMAGES:
            gun_img = cload_img(GUN_IMAGES[gun]).convert_alpha()
            gun_img = pg.transform.scale(gun_img, (32, 32))
            self.gun_images[gun] = gun_img

        self.bullet_images = {}
        self.pistol_bullet_img = pg.Surface((7, 7))
        self.bullet_images['pistol'] = self.pistol_bullet_img
        self.shotgun_bullet_img = pg.Surface((3, 3))
        self.bullet_images['shotgun'] = self.shotgun_bullet_img
        self.uzi_bullet_img = pg.Surface((4, 4))
        self.bullet_images['uzi'] = self.uzi_bullet_img
        self.gun_flashes = []

        # TODO adapt to web ctx
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(
                cload_img(img).convert_alpha()
            )

        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = cload_img(ITEM_IMAGES[item]).convert_alpha()

        self.splat_images = []
        # TODO retablir giclées de sang, sprsheet si possible?
        # for img in SPLAT_IMAGES:
        #     i = pg.image.load(path.join(self.img_folder, img)).convert_alpha()
        #     i.set_colorkey(BLACK)
        #     i = pg.transform.scale(i, (64, 64))
        #     self.splat_images.append(i)

        # lighting effect
        self.fog = pg.Surface(pyv.get_surface().get_size())
        self.fog.fill(NIGHT_COLOR)

        self.light_mask = cload_img(LIGHT_MASK).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

        # PRE-load sounds
        if not NO_SOUND:
            pg.mixer.music.load(SNDPATH+MENU_MUSIC)
            self.effects_sounds = {}
            for snd_type in EFFECTS_SOUNDS:
                snd = pg.mixer.Sound(SNDPATH+EFFECTS_SOUNDS[snd_type])
                snd.set_volume(self.soundfx_lvl)
                self.effects_sounds[snd_type] = snd
                self.all_sounds.append(snd)

            self.weapon_sounds = {}
            for weapon in WEAPON_SOUNDS:
                self.weapon_sounds[weapon] = []
                for snd in WEAPON_SOUNDS[weapon]:
                    s = pg.mixer.Sound(SNDPATH+snd)
                    s.set_volume(0.5)
                    self.weapon_sounds[weapon].append(s)
                    self.all_sounds.append(s)

            self.player_hit_sounds = []
            for snd in PLAYER_HIT_SOUNDS:
                s = pg.mixer.Sound(SNDPATH+snd)
                self.player_hit_sounds.append(s)
                self.all_sounds.append(s)

            self.zombie_moan_sounds = []
            for snd in ZOMBIE_MOAN_SOUNDS:
                s = pg.mixer.Sound(SNDPATH+snd)
                s.set_volume(0.1)
                self.zombie_moan_sounds.append(s)
                self.all_sounds.append(s)

            self.zombie_death_sounds = []
            for snd in ZOMBIE_DEATH_SOUNDS:
                s = pg.mixer.Sound(SNDPATH+snd)
                self.zombie_death_sounds.append(s)
                self.all_sounds.append(s)

    # -------------------------------------------
    #  these three methods have been disabled
    # -------------------------------------------
    def toggle_fullscreen(self):
        pass

    def show_story_screen(self, unknown_arg):
        pass

    def save_progress(self):
        pass

    def load_level(self, stats=None):
        # level_name = 'tutorial.tmx' <-- previously this was the default val.

        self.game_over = False
        self.all_sprites = pg.sprite.LayeredUpdates()  # Group()
        self.walls = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.landmines = pg.sprite.Group()
        self.explosions = pg.sprite.Group()
        # Grab our game layout file (map)
        # TODO support multi-level
        #  self.current_lvl = level_name
        self.current_lvl = 'level1.tmx'

        self.player_img = cload_img(
            LEVELS[self.current_lvl]['plyr']
        ).convert_alpha()  # Surface
        self.objective = LEVELS[self.current_lvl]['objective']
        self.story = LEVELS[self.current_lvl]['story']

        self.map = tilemap.CustomTiledMap('assets/maps/level1.tmj', 'assets/')  # mapspath, level_filename)

        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.texts = pg.sprite.Group()  # Created sprite group of texts, and apply the camera on them
        # Amount of comms needed to beat level
        self.comms_req = 0

        # load everything on map
        for tile_object in self.map.objects:
            obj_center = pg.math.Vector2(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                if stats:
                    self.player = Player(self, obj_center.x, obj_center.y, stats)
                else:
                    self.player = Player(self, obj_center.x, obj_center.y)
            elif tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            elif tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)  # pass
            elif tile_object.name == 'runner':
                Runner(self, obj_center.x, obj_center.y)
            elif tile_object.name == 'tower':
                Tower(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            elif tile_object.name in ITEM_IMAGES.keys():
                if tile_object.name == 'bonus':
                    ratio = (32, 32)
                    if tile_object.type == 'x':
                        BonusItem(self, obj_center, 'x', ratio)
                    else:
                        BonusItem(self, obj_center, 'y', ratio)
                    continue
                elif tile_object.name == 'health':
                    ratio = (32, 32)
                elif tile_object.name == 'comms':
                    ratio = (48, 48)
                    self.comms_req += 1
                elif tile_object.name in GUN_IMAGES:
                    ratio = (48, 48)
                elif tile_object.name == 'pistol_ammo' or tile_object.name == 'shotgun_ammo' \
                        or tile_object.name == 'uzi_ammo':
                    ratio = (32, 32)
                elif tile_object.name == 'landmine':
                    ratio = (32, 32)
                Item(self, obj_center, tile_object.name, ratio)
            elif tile_object.type == 'text':  # putting text in object name
                IngameText(self, tile_object.x, tile_object.y, tile_object.name)

        self.camera = tilemap.Camera(self.map.width, self.map.height)  # , WINDOW_WIDTH, WINDOW_HEIGHT)
        # self.draw_debug = False
        self.paused = False

        if not NO_SOUND:
            pg.mixer.music.stop()

        self.show_story_screen(LEVELS[self.current_lvl]['story'])

        if not NO_SOUND:
            # if self.current_lvl == 'tutorial.tmx':
            self.current_music = LEVELS[self.current_lvl]['music']
            self.effects_sounds['level_start'].play()
            #    self.current_music = BG_MUSIC
            # elif self.current_lvl == 'level1.tmx':
            #    self.current_music = LVL1_MUSIC
            pg.mixer.music.load(SNDPATH+self.current_music)
            pg.mixer.music.play(loops=-1)

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)

        # Mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        if not self.player.is_damaged and hits:
            self.player.got_hit()
            self.player.pos += pg.math.Vector2(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
            for hit in hits:
                self.player.health -= MOB_DAMAGE
                if not NO_SOUND:
                    if random() <= 0.9:
                        choice(self.player_hit_sounds).play()
                hit.vel = pg.math.Vector2(0, 0)

        # Player touches explosion
        hits = pg.sprite.spritecollide(self.player, self.explosions, False, collide_hit_rect)
        if not self.player.is_damaged and hits:
            self.player.got_hit()
            self.player.pos -= pg.math.Vector2(LANDMINE_KNOCKBACK, 0).rotate(self.player.rot)
            for hit in hits:
                self.player.health -= LANDMINE_DAMAGE
                if not NO_SOUND:
                    if random() < 0.9:
                        choice(self.player_hit_sounds).play()

                hit.vel = pg.math.Vector2(0, 0)
        if self.player.health <= 0:
            self.save_progress()
            self.playing = False
            self.game_over = True

        # Bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            # Multiply dmg by amount of bullets that hit the mob using len(hits[hit]) keep in mind hits is a dict
            # hit.health -= WEAPONS[self.player.curr_weapon]['damage'] * len(hits[hit])  # TODO: ensure correctness
            # Purpose for doing it this way to ensure that the bullet damage doesn't depend on which gun the player is
            # holding
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            mob.vel = pg.math.Vector2(0, 0)
        # Mobs touch mine
        hits = pg.sprite.groupcollide(self.mobs, self.landmines, False, True)
        if hits:
            if not NO_SOUND:
                self.effects_sounds['explosion'].play()

        for mob in hits:
            Explosion(self, mob.pos)
        # Mobs touch explosion
        hits = pg.sprite.groupcollide(self.mobs, self.explosions, False, False)
        for mob in hits:
            mob.health -= LANDMINE_DAMAGE + self.player.stats['dmg_bonus']
            mob.vel = pg.math.Vector2(0, 0)
        # Player touches item
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:  # TODO: Put sounds in an object instead of a dictionary
            if hit.type == 'health' and self.player.health < PLAYER_MAX_HEALTH:
                if not NO_SOUND:
                    self.effects_sounds['health_up'].play()  # TODO: Find different sound
                self.player.health = min(self.player.health + HEALTH_PICKUP_AMT, PLAYER_MAX_HEALTH)
                hit.kill()
            elif hit.type == 'shotgun':
                hit.kill()
                if not NO_SOUND:
                    self.effects_sounds['gun_pickup'].play()
                self.player.weapons.append('shotgun')
                self.player.weapon_selection += 1
                self.player.curr_weapon = 'shotgun'
                self.player.ammo['shotgun_ammo'] += SHOTGUN_AMMO_PICKUP_AMT + self.player.stats['ammo_bonus']
            elif hit.type == 'uzi':
                hit.kill()
                if not NO_SOUND:
                    self.effects_sounds['gun_pickup'].play()
                self.player.weapons.append('uzi')
                self.player.weapon_selection += 1
                self.player.curr_weapon = 'uzi'
                self.player.ammo['uzi_ammo'] += UZI_AMMO_PICKUP_AMT + self.player.stats['ammo_bonus']
            elif hit.type == 'pistol_ammo':
                if hit.visible:
                    hit.make_invisible()
                    self.player.ammo['pistol_ammo'] += PISTOL_AMMO_PICKUP_AMT + self.player.stats['ammo_bonus']
                    if not NO_SOUND:
                        self.effects_sounds['ammo_pickup'].play()
            elif hit.type == 'shotgun_ammo':
                hit.kill()
                self.player.ammo['shotgun_ammo'] += SHOTGUN_AMMO_PICKUP_AMT + self.player.stats['ammo_bonus']
                if not NO_SOUND:
                    self.effects_sounds['ammo_pickup'].play()
            elif hit.type == 'uzi_ammo':
                hit.kill()
                self.player.ammo['uzi_ammo'] += UZI_AMMO_PICKUP_AMT + self.player.stats['ammo_bonus']
                if not NO_SOUND:
                    self.effects_sounds['ammo_pickup'].play()
            elif hit.type == 'landmine':
                hit.kill()
                self.player.ammo['landmines'] += 1  # Not getting any bonus stats for mines ;)
                if not NO_SOUND:
                    self.effects_sounds['ammo_pickup'].play()
            elif hit.type == 'comms':
                hit.kill()
                self.player.comms += 1
                if not NO_SOUND:
                    self.effects_sounds['item_pickup'].play()
                if self.current_lvl == 'tutorial.tmx':
                    IngameText(self, 2000, 200, "Pistol ammo regenerates...")

        # Bullet touches BonusItem
        hits = pg.sprite.groupcollide(self.items, self.bullets, False, False)
        for hit in hits:
            if isinstance(hit, BonusItem):
                hit.kill()
                hit.activate(self.player)
                self.player.stats['bonuses'] += 1
        # Check if we beat brought comms to tower
        if self.objective == 'return_comms':
            hits = pg.sprite.spritecollide(self.player, self.towers, False, False)
            for hit in hits:
                if self.player.comms >= self.comms_req:
                    self.level_complete = True
        elif self.objective == 'kill_all_zombies':
            if len(self.mobs) <= 0:
                self.level_complete = True

        if self.level_complete:  # ------ GO TO NEXT LEVEL ------
            print('----------------------------')
            print('  LEVEL COMPLETED')
            print('----------------------------')

            # self.player.kill()
            if not NO_SOUND:
                pg.mixer.music.stop()

            # TODO multi-level support
            # self.level_complete = False
            # if self.current_lvl == 'tutorial.tmx':
            #     self.load_level('level1.tmx', self.player.stats)
            # elif self.current_lvl == 'level1.tmx':
            #     self.playing = False
            #     self.current_lvl = 'ending'

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, TILESIZE):
            pg.draw.line(self.screen, WHITE, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, TILESIZE):
            pg.draw.line(self.screen, WHITE, (0, y), (WINDOW_WIDTH, y))

    def draw_health(self, x, y, health_pct):
        surface = self.screen
        if health_pct < 0:
            health_pct = 0
        fill = health_pct * PLAYER_HEALTH_BAR_WIDTH
        outline_rect = pg.Rect(x, y, PLAYER_HEALTH_BAR_WIDTH, PLAYER_HEALTH_BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, PLAYER_HEALTH_BAR_HEIGHT)
        if health_pct > 0.65:
            col = GREEN
        elif health_pct > 0.45:
            col = YELLOW
        else:
            col = RED
        pg.draw.rect(surface, col, fill_rect)
        pg.draw.rect(surface, WHITE, outline_rect, 2)

    def render_fog(self):
        # draw the light mask (gradient) onto the fog image
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply_sprite(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)  # mask -> light_rect
        # BLEND_MULT blends somehow by multiplying adjacent pixels color's (int values)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def draw_scene(self):
        # pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))

        # self.draw_grid()
        for sprite in self.all_sprites:
            # if isinstance(sprite, Mob):  # I put this in the Mob.update instead
            #    sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply_sprite(sprite))
            if self.draw_debug:
                if hasattr(sprite, 'hit_rect'):
                    rect_drawn = self.camera.apply_rect(sprite.hit_rect)
                    adhoc_r = rect_drawn
                elif hasattr(sprite, 'pos'):
                    adhoc_r = (
                        self.camera.camera[0] + sprite.pos[0] - (sprite.rect[2] / 2),
                        self.camera.camera[1] + sprite.pos[1] - (sprite.rect[3] / 2),
                        sprite.rect[2],
                        sprite.rect[3]
                    )
                else:
                    adhoc_r = None
                if adhoc_r:
                    pg.draw.rect(self.screen, RED, adhoc_r, 1)

        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(wall.rect), 1)

        # Draw player's rect. Good for debugging.   Thickness of 2
        # pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)

        if not NO_FOG:
            self.render_fog()
        # if self.is_night:
        #     self.render_fog()
        self.draw_health(5, 5, self.player.health / PLAYER_MAX_HEALTH)

        # Display current weapon
        self.screen.blit(self.gun_images[self.player.curr_weapon], (10, 25))
        # Display current ammo
        curr_weapon_ammo_amt = self.player.get_ammo(self.player.curr_weapon)
        self.draw_text(' - {}'.format(curr_weapon_ammo_amt), self.hud_font, 30, BLACK, 45, 30, align='nw')

        # display zombies left
        self.draw_text(
            'ZOMBIES - {}'.format(len(self.mobs)), self.hud_font, 30, WHITE, WINDOW_WIDTH - 10, 10, align='ne'
        )


# todo fix
# @katasdk.tag_gameenter
def game_enter(vmst=None):
    global g, glclock, basefont
    pyv.init(1)
    basefont = pg.font.Font(None, 29)
    glclock = pyv.pygame.time.Clock()
    g = GameWorld()
    g.screen = pyv.get_surface()
    g.load_data()
    g.load_level()


# tod fix
# @katasdk.tag_gameupdate
def game_update(timeinfo=None):
    global saved_t
    # if we dont do this, the player cannot move
    # g.dt = g.clock.tick(FPS) / 1000
    if saved_t:
        g.dt = timeinfo - saved_t
    else:
        g.dt = 0
    saved_t = timeinfo

    # ------------------------------
    #  future ctrl
    # ------------------------------
    # catch all events here
    for event in pg.event.get():
        if event.type == pg.QUIT:
            g.game_over = True

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_g:
                g.draw_debug = not g.draw_debug
                print('debug mode: {}'.format(g.draw_debug))
            if event.key == pg.K_p:
                g.paused = not g.paused
                print('pause: {}'.format(g.paused))

            # if event.key == pg.K_j:
            #     g.is_night = not g.is_night
            #     print('night mode: {}'.format(g.is_night))

            # Not the best design, but for convenience putting player action keys here
            if event.key == pg.K_c:
                g.player.change_weapon()
            if event.key == pg.K_x:
                g.player.place_mine()
            if event.key == pg.K_F4:
                g.toggle_fullscreen()

    g.update()
    if g.player.wanna_exit:
        return WARP_BACK_SIG

    g.draw_scene()
    lbl = basefont.render(
        '{:.2f}'.format(glclock.get_fps()),
        True,
        (250, 13, 55),
        (0, 0, 0)
    )
    screen = pyv.get_surface()
    screen.blit(lbl, (screen.get_size()[0] - 96, 16))

    pyv.flip()
    glclock.tick(pyv.vars.max_fps)


# todo fix
# @katasdk.tag_gameexit
def game_exit(vmstate=None):
    pyv.close_game()


# ----------------
#  add-on for testing using pyv only
# ----------------
if not WEBCTX:
    game_enter(None)
    gameover = False

    while not gameover:
        game_update(time.time())

    game_exit(None)
