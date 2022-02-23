"""
legacy of the first GAME ENGINE
  designed by wkta
(the "coremon engine" 2018-2020)

contact author: thomas@gaudia-tech.com

 the structure has been slightly modified in 2021 to become web-compatible

License LGPL3
"""
# from .... import engine as kataen
# from . import cgmconf
# from .foundation import events as kevent
# from .foundation.events import DeadSimpleManager
# GameTicker = kataen
# from .foundation.runners import GameTicker, StackBasedGameCtrl

from ... import _hub as injec
from ...foundation import shared


engine_is_init = False
headless_mode = False
game_ticker = None
SCR_SIZE = None  # virtual scr size
K_LEGACY, K_OLDSCHOOL, K_HD = range(79, 79 + 3)
_multistate = False
_stack_based_ctrl = None


def legacyinit(gfxmode_str, caption=None, maxfps=60):
    global engine_is_init, game_ticker, SCR_SIZE
    pygame_module = injec.pygame

    pygame_module.init()
    if not shared.RUNS_IN_WEB_CTX:
        pygame_module.mixer.init()
    else:
        pygame_module.time.do_fake_init()

    engine_is_init = True

    # we defined 3 canonical modes for display:
    # 'legacy' (upscaling x3), 'oldschool', (upscaling x2)
    # 'hd' & with a pixel to canvas mapping

    str_to_code = {
        'super_retro': K_LEGACY,
        'old_school': K_OLDSCHOOL,
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

    if shared.RUNS_IN_WEB_CTX:
        print('call display set_mode with arg: ')
        print(taille_surf_dessin)
        pygame_surf_dessin = pygame_module.display.set_mode(taille_surf_dessin)
    else:
        pgscreen = pygame_module.display.set_mode(shared.CONST_SCR_SIZE)
        pygame_surf_dessin = pygame_module.surface.Surface(taille_surf_dessin)
        injec.core.set_realpygame_screen(pgscreen)

    result = upscaling[chosen_mode]
    injec.core.set_virtual_screen(pygame_surf_dessin, upscaling[chosen_mode])

    if upscaling[chosen_mode] is not None:
        print('upscaling x{}'.format(upscaling[chosen_mode]))

    if not shared.RUNS_IN_WEB_CTX:
        print('<->context: genuine Pygame')
        if caption is None:
            pygame_module.display.set_caption(
                'Made using KataSDK'
            )
        else:
            pygame_module.display.set_caption(caption)

        injec.event.create_manager()
        game_ticker = injec.event.GameTicker(maxfps)

    else:
        import katagames_sdk.pygame_emu.overlay as overlay
        print('<->context: Web')
        manager_4web = overlay.upgrade_evt_manager(pygame_module)
        print('overlay ok')
        injec.event.gl_unique_manager = manager_4web
        game_ticker = overlay.WebCtxGameTicker()

    return result  # can be None, if no upscaling applied


def retrieve_game_ctrl():
    global engine_is_init, game_ticker, _multistate, _stack_based_ctrl
    assert engine_is_init

    if _multistate:
        return _stack_based_ctrl
    else:
        return game_ticker


def tag_multistate(allstates, use_katagames_env, glvars_pymodule, providedst_classes=None):
    global game_ticker, _stack_based_ctrl, _multistate

    _multistate = True

    if use_katagames_env:
        temp_var = ' ???'  # TODO fix this case /!\ the kata base auth auth screen needs to be def somewhere else
        raise NotImplementedError
    else:
        temp_var = None

    _stack_based_ctrl = injec.event.StackBasedGameCtrl(
        game_ticker, allstates, glvars_pymodule, providedst_classes, temp_var
    )


def get_manager():
    return injec.gl_unique_manager


def old_cleanup():
    global engine_is_init
    assert engine_is_init
    injec.event.gl_unique_manager.hard_reset()

    injec.pygame.mixer.quit()
    injec.pygame.quit()

    engine_is_init = False
    print('cleanup: OK')


# -------------------------------------------------
#    nouveautés 2021 - 2022
# -------------------------------------------------

# _curr_state = DummyState(-1, 'dummy_gs')
# _loaded_states = {
#     -1: _curr_state
# }
#
# state_stack = Stack()


def declare_states(assoc_code_gs, new_state_id=None):
    global _loaded_states
    print('declaring states...')
    print(str(assoc_code_gs))
    print()

    # verif
    for ke, gs in assoc_code_gs.items():
        if ke in _loaded_states.keys():
            print('[Warning] gamestate code {} was already taken. Overriding state(risky)...'.format(ke))
            del _loaded_states[ke]
    _loaded_states.update(assoc_code_gs)
    # can change state instant
    if new_state_id is not None:
        print('wish new state:'+str(new_state_id))
        _new_state(new_state_id)


def _new_state(gs_code):
    global _curr_state, state_stack, _loaded_states

    print('new state call')
    print(gs_code)
    print(str(_loaded_states))

    _curr_state.release()
    state_stack.pop()

    state_stack.push(gs_code)
    _loaded_states[gs_code].enter()
