"""
this demo is a collab - OPEN-SOURCE - Public domain

Authors, sorted by reverse chronological order:

 -moonbak a.k.a. Tom founder of KataGames - github.com/wkta
 -Renfred Harper
 -Richard Jones (authored the 1st prototype. This includes XML/TMX parsing)

My goal here, in 2022-2023:
to provide a platformer game template for kengi, refe to:
github.com/gaudiatech/kengi so every game dev can learn more,
discover cool stuff that saves time if youre already a pygame user.
"""
import pyved_engine as pyv
pyv.bootstrap_e()


from sprites import Player, Enemy


bg_sprite = None
game = None


# -----------------------------------------
#  two proc used by the game, so the player can respawn
# -----------------------------------------
def _session_reset(first_run=False):  # TODO improve design
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


@pyv.declare_begin
def prep_game(vmst=None):
    global game, bg_sprite

    HELP_MSG = 'CONTROLS: Left/right arrow key to move | left Ctrl key to shoot | Spacebar to jump'
    print(HELP_MSG)

    pyv.init()

    tilemap_obj = pyv.tmx.data.load_tmx('level.tmx')  # -> Tilemap instance
    li_assets = ['enemy.png', 'missile.png', 'player-right.png', 'player-left.png']
    map_bg_name = ''
    if tilemap_obj.background:
        map_bg_name, map_bg_file = pyv.util.path_to_img_infos(tilemap_obj.background['img_path'])
        li_assets.append(map_bg_file)
    pyv.preload_assets({  # chargement ressources
        'images': li_assets,
        # 'sounds': []
    }, prefix_asset_folder='assets/')
    viewport = pyv.tmx.misc.Viewport(tilemap_obj, (0, 0), pyv.vars.disp_size)

    game = pyv.Objectifier(**{
        'tilemap': tilemap_obj,
        'viewport': viewport,
        'player': None,
        'sprites': None,
        'enemies': None
    })

    # convert bg to a sprite (a sprite is more convenient, as we can repeat/loop it easily)
    if tilemap_obj.background:
        # turn background image to
        tmpbg = pyv.pygame.sprite.Sprite()
        img = pyv.vars.images[map_bg_name]
        tmp_img = pyv.pygame.transform.scale(img, pyv.vars.disp_size)
        tmpbg.image = tmp_img
        tmpbg.rect = tmpbg.image.get_rect()
        tmpbg.rect.left = -16 + tilemap_obj.background['offsetx']
        tmpbg.rect.top = 0

        print('bg found in .tmx file: conversion to Sprite ->Ok!')
        bg_sprite = tmpbg

    # reset gamesession data
    _session_reset(first_run=True)


@pyv.declare_update
def update_g(time_info=None):
    global game

    while True:  # TODO can i do better than this dirty 2nd-order gameloop?
        dt = pyv.vars.clock.tick(30)

        for event in pyv.fetch_events():
            if event.type == pyv.pygame.QUIT:
                pyv.vars.gameover = True
                return
            if event.type == pyv.pygame.KEYDOWN and event.key == pyv.pygame.K_ESCAPE:
                pyv.vars.gameover = True
                return

        # logic update
        if game.player.is_dead:
            print('** you died **')
            _session_reset()
            continue

        game.tilemap.update(dt / 1000., game)

        # - display
        scr = pyv.vars.screen
        scr.blit(bg_sprite.image, (0, 0))
        game.viewport.draw(scr)

        pyv.flip()  # need to flip manually, cause its a 2nd-order gameloop


@pyv.declare_end
def cleanup(vmst=None):
    print('clean exit!')
    pyv.close_game()


pyv.run_game()
