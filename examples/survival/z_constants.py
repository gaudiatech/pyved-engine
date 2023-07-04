import pyved_engine as pyv
pyv.bootstrap_e()


pg = pyv.pygame


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
FONT_NAME = 'arial'

# Ensure no partial squares with these values
WINDOW_WIDTH = 1024  # 16 * 64 or 32 * 32 or 64 * 16
WINDOW_HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
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
PLAYER2_IMG = 'hitman_gun.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)  # needs to be Rect to get center (not Surface)
# By default, player facing right, so offset the bullet 30 to the right (x) and 10 down (y)
BARREL_OFFSET = pg.math.Vector2(30, 10)
PLAYER_HEALTH_BAR_HEIGHT = 20
PLAYER_HEALTH_BAR_WIDTH = 100

# Weapon settings
# BULLET_IMG = 'bullet.png' # Using Surface instead.
# MAYBE: Create a Weapon class instead of dictionaries in our settings file
WEAPONS = {'pistol': {
    'bullet_speed': 750,
    'bullet_lifetime': 1250,
    'fire_rate': 425,
    'kickback': 200,
    'bullet_spread': 6,
    'damage': 10,
    'bullet_count': 1,
    'bullet_usage': 1

}, 'shotgun': {
    'bullet_speed': 500,
    'bullet_lifetime': 500,
    'fire_rate': 1000,
    'kickback': 500,
    'bullet_spread': 24,
    'damage': 8,
    'bullet_count': 5,
    'bullet_usage': 1
}, 'uzi': {
    'bullet_speed': 1000,
    'bullet_lifetime': 750,
    'fire_rate': 175,
    'kickback': 300,
    'bullet_spread': 15,
    'damage': 7,
    'bullet_count': 1,
    'bullet_usage': 1
}}
LANDMINE_DAMAGE = 35
LANDMINE_KNOCKBACK = 50

# Mob settings
MOB_IMG = 'zombie1_hold.png'
MOB_SPEEDS = [220, 240, 260]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_DAMAGE = 10
MOB_KNOCKBACK = 25
MOB_AVOID_RADIUS = 70  # in px
MOB_DETECT_RADIUS = 325

# Runner settings
RUNNER_IMG = 'zombie2_hold.png'
RUNNER_SPEEDS = [350, 365]
RUNNER_HIT_RECT = pg.Rect(0, 0, 30, 30)
RUNNER_DAMAGE = 15
RUNNER_KNOCKBACK = 30
RUNNER_AVOID_RADIUS = 45  # in px
RUNNER_DETECT_RADIUS = 350

# Items
ITEM_IMAGES = {
    "health": "health_icon.png",
    "pistol_ammo": "pistol_ammo.png",
    "shotgun_ammo": "shotgun_ammo.png",
    "uzi_ammo": "uzi_ammo.png",
    "landmine": "mine_icon.png",
    "bonus": "bonus.png",
    "comms": "comms_icon.png",
    "shotgun": "shotgun.png",
    "pistol": "pistol.png",
    "uzi": "uzi.png",
    "placed_mine": "landmine.png",
    "tower": "cell_tower.png"
}

GUN_IMAGES = {
    "pistol": "pistol.png",
    "shotgun": "shotgun.png",
    "uzi": "uzi.png"
}

# Item effectiveness
HEALTH_PICKUP_AMT = 25
PISTOL_AMMO_PICKUP_AMT = 6
SHOTGUN_AMMO_PICKUP_AMT = 6
UZI_AMMO_PICKUP_AMT = 14

# Effects
MUZZLE_FLASHES = ["whitePuff15.png", "whitePuff16.png", "whitePuff17.png", "whitePuff18.png"]
FLASH_DURATION = 40  # ms
SPLAT_IMAGES = ['blood-splatter1.png', 'blood-splatter3.png', 'blood-splatter4.png']

ITEM_BOB_RANGE = 50
ITEM_BOB_SPEED = 3

DAMAGE_ALPHA = [i for i in range(0, 255, 20)]
ITEM_ALPHA = [i for i in range(0, 255, 2)]
ITEM_FADE_MIN = 50
ITEM_FADE_MAX = 245
NIGHT_COLOR = (200, 200, 200)
LIGHT_RADIUS = (350, 350)
LIGHT_MASK = 'light_350_med.png'

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
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
                      'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav']
ZOMBIE_DEATH_SOUNDS = ['splat-15.wav']
WEAPON_SOUNDS = {
    'pistol': ['pistol.wav'],
    'shotgun': ['shotgun.wav'],
    'uzi': ['uzi.wav'],
    'empty': ['empty_gun.wav']
}
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
