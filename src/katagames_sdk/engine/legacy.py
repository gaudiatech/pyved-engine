"""
legacy of the first GAME ENGINE
  designed by wkta
(the "coremon engine" 2018-2020)

contact author: thomas@gaudia-tech.com

 the structure has been slightly modified in 2021 to become web-compatible

License LGPL3
"""
from .foundation import conf_eng as cgmconf
from .foundation import events as kevent
from .foundation.events import DeadSimpleManager
from .foundation.runners import GameTicker, StackBasedGameCtrl


engine_is_init = False
headless_mode = False
game_ticker = None
SCR_SIZE = None  # virtual scr size
K_LEGACY, K_OLDSCHOOL, K_HD = range(79, 79+3)
_multistate = False
_stack_based_ctrl = None


def legacyinit(pygame_module, gfxmode_str, caption=None, maxfps=60):
    global engine_is_init, game_ticker, SCR_SIZE

    pygame_module.init()
    if not cgmconf.runs_in_web:
        pygame_module.mixer.init()
    else:
        pygame_module.time.do_fake_init()
    
    engine_is_init = True

    # we defined 3 canonical modes for display:
    # 'legacy' (upscaling x3), 'oldschool', (upscaling x2)
    # 'hd' & with a pixel to canvas mapping

    str_to_code = {
        'superretro': K_LEGACY,
        'oldschool': K_OLDSCHOOL,
        'hd': K_HD
    }
    chosen_mode = str_to_code[gfxmode_str]

    drawspace_size = {
        K_LEGACY: (320, 180),
        K_OLDSCHOOL: (480, 270),
        K_HD: (960, 540)
    }
    upscaling = {
        K_LEGACY: 3.0,
        K_OLDSCHOOL: 2.0,
        K_HD: None
    }
    taille_surf_dessin = drawspace_size[chosen_mode]

    if cgmconf.runs_in_web:
        print('call display set_mode with arg: ')
        print(taille_surf_dessin)
        pygame_surf_dessin = pygame_module.display.set_mode(taille_surf_dessin)
    else:
        pgscreen = pygame_module.display.set_mode(cgmconf.CONST_SCR_SIZE)
        pygame_surf_dessin = pygame_module.surface.Surface(taille_surf_dessin)
        cgmconf.set_realpygame_screen(pgscreen)

    result = upscaling[chosen_mode]
    cgmconf.set_virtual_screen(pygame_surf_dessin, upscaling[chosen_mode])

    if upscaling[chosen_mode] is not None:
        print('upscaling x{}'.format(upscaling[chosen_mode]))

    if not cgmconf.runs_in_web:
        print('<->context: genuine Pygame')
        if caption is None:
            pygame_module.display.set_caption(
                'Made using KataSDK'
            )
        else:
            pygame_module.display.set_caption(caption)

        kevent.gl_unique_manager = DeadSimpleManager(pygame_module)
        game_ticker = GameTicker(pygame_module, maxfps)

    else:
        import katagames_sdk.pygame_emu.overlay as overlay
        print('<->context: Web')
        manager_4web = overlay.upgrade_evt_manager(pygame_module)
        print('overlay ok')
        kevent.gl_unique_manager = manager_4web
        game_ticker = overlay.WebCtxGameTicker(pygame_module)

    return result  # can be None, if no upscaling applied


def retrieve_game_ctrl():
    global engine_is_init, game_ticker, _multistate, _stack_based_ctrl
    assert engine_is_init

    if _multistate:
        return _stack_based_ctrl
    else:
        return game_ticker


def tag_multistate(allstates, glvars_pymodule, use_katagames_env, providedst_classes=None):
    global game_ticker, _stack_based_ctrl, _multistate
    _multistate = True
    _stack_based_ctrl = StackBasedGameCtrl(
        game_ticker, allstates, glvars_pymodule, use_katagames_env, providedst_classes
    )


def get_manager():
    return kevent.gl_unique_manager


def cleanup():
    global engine_is_init
    assert engine_is_init
    pygame_pym = cgmconf.pygame

    if not cgmconf.runs_in_web:
        kevent.gl_unique_manager.hard_reset()
        cgmconf.pygame_screen = None

        pygame_pym.mixer.quit()
        pygame_pym.quit()
        engine_is_init = False
        print('clean exit: OK')
    else:
        print('never ending gameloop (web context)')
