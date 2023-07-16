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
import pyved_engine as pyv
from pyved_engine import *
from sprites import Player, Enemy


# bg = None
# map_bg_name = None
# bg_sprite = None
# first_run = None
# wanna_quit = False
# t_last_refresh = None


game = None


# -----------------------------------------
#  two proc used by the game, so the player can respawn
# -----------------------------------------
def _session_reset():  # TODO improve design
    global game

    tilemap_obj = game.tilemap

    if not first_run:  # how to write this better?
        tilemap_obj.layers.pop()
        tilemap_obj.layers.pop()

    sprites = pyv.tmx.misc.SpriteLayer()
    game.sprites = sprites

    start_cell = tilemap_obj.layers['triggers'].find('player')[0]
    print(start_cell)

    player_obj = Player((start_cell.px, start_cell.py), sprites)
    game.player = player_obj

    tilemap_obj.layers.append(sprites)
    enemies = pyv.tmx.misc.SpriteLayer()
    game.enemies = enemies

    for enemy in tilemap_obj.layers['triggers'].find('enemy'):
        eo = Enemy((enemy.px, enemy.py), enemies)
        eo.ref_player = player_obj
    tilemap_obj.layers.append(enemies)


def _game_session():
    global first_run, wanna_quit, game
    first_run = False
    ongoing_session = True

    while ongoing_session:
        dt = pyv.vars.clock.tick(30)

        for event in pyv.fetch_events():
            if event.type == QUIT:
                wanna_quit = True
                return
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                wanna_quit = True
                return

        # logic update
        if game.player.is_dead:
            ongoing_session = False
            print('** you died **')
        else:
            game.tilemap.update(dt / 1000., game)

        # - display
        scr = pyv.vars.screen
        scr.blit(bg.image, (0, 0))
        game.viewport.draw(scr)
        pyv.flip()

first_run = True
def launch():
    global wanna_quit, map_bg_name, first_run, game, bg_sprite, bg, first_run
    pyv.init()

    tilemap_obj = pyv.tmx.data.load_tmx('level.tmx')  # -> Tilemap instance
    li_assets = ['enemy.png', 'missile.png', 'player-right.png', 'player-left.png']

    if tilemap_obj.background:
        map_bg_name, map_bg_file = pyv.util.path_to_img_infos(tilemap_obj.background['img_path'])
        li_assets.append(map_bg_file)

    # initialisation pour charger des ressources (snd, images)
    pyv.preload_assets({
        'images': li_assets,
        # 'sounds': ['tir1.wav', 'propulseur.wav', 'EXPLOSION.mp3', 'Victoire.mp3', 'musique.mp3']
    }, prefix_asset_folder='assets/')

    print('--------- controls ----------')
    print('left/right arrows to move |  Left Ctrl key to shoot | Spacebar to jump')
    print()
    wanna_quit = False

    scr_size = pyv.vars.disp_size
    viewport = pyv.tmx.misc.Viewport(tilemap_obj, (0, 0), scr_size)

    game = pyv.Objectifier(**{
        'tilemap': tilemap_obj,
        'player': None,
        'sprites': None,
        'viewport': viewport,
        'enemies': None
    })

    # - search for background
    if tilemap_obj.background:
        print('info about bg found in .tmx file, ok!')
        # turn background image to a sprite, so we can repeat it easily
        bg = pyv.pygame.sprite.Sprite()
        img = pyv.vars.images[map_bg_name]
        tmp_img = pyv.pygame.transform.scale(img, scr_size)

        bg.image = tmp_img
        bg.rect = bg.image.get_rect()
        bg.rect.left = -16 + tilemap_obj.background['offsetx']
        bg.rect.top = 0
        bg_sprite = bg

    _session_reset()
    while not wanna_quit:
        _game_session()  # TODO can i do better thant a level-2 game loop?
        _session_reset()
    pyv.close_game()


launch()
