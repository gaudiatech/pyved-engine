"""
(~*~ legacy code ~*~)
AUTHOR INFO
 Thomas I. cf. https://github.com/wkta
contact author: thomas@gaudia-tech.com

LICENSE INFO
 for the whole legacy folder: LGPL3

It's the legacy of the first GAME ENGINE named
coremon engine, coded by Tom during 2018-2020.
the structure has been modified later,
in 2021 to become web-compatible
"""


from .. import _hub as injec
from ..foundation import shared
from ..__version__ import ENGI_VERSION as registered_vernum


engine_is_init = False
headless_mode = False
game_ticker = None
SCR_SIZE = None  # virtual scr size
K_LEGACY, K_OLDSCHOOL, K_HD, K_CUSTOM = range(79, 79 + 4)
_multistate = False
_stack_based_ctrl = None


def legacyinit(gfxmode_str, caption, maxfps, screen_dim=None):
    global engine_is_init, game_ticker, SCR_SIZE

    if engine_is_init:
        raise ValueError('legacyinit called while engine_is_init==True')

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
        'hd': K_HD,
        'custom': K_CUSTOM
    }
    chosen_mode = str_to_code[gfxmode_str]

    bw, bh = shared.CONST_SCR_SIZE
    drawspace_size = {
        K_HD: (bw, bh),
        K_OLDSCHOOL: (bw//2, bh//2),
        K_LEGACY: (bw // 3, bh // 3),
    }
    upscaling = {
        K_LEGACY: 3.0,
        K_OLDSCHOOL: 2.0,
        K_HD: None,
        K_CUSTOM: None
    }
    if chosen_mode == K_CUSTOM:
        if screen_dim is None:
            raise ValueError('custom mode for gfx, but no screen_dim found!')
        taille_surf_dessin = screen_dim
    else:
        taille_surf_dessin = drawspace_size[chosen_mode]

    if shared.RUNS_IN_WEB_CTX:
        print('call display set_mode with arg: ')
        print(taille_surf_dessin)
        pygame_surf_dessin = pygame_module.display.set_mode(taille_surf_dessin)
    else:
        if chosen_mode == K_CUSTOM:
            pgscreen = pygame_module.display.set_mode(taille_surf_dessin)
        else:
            pgscreen = pygame_module.display.set_mode(shared.CONST_SCR_SIZE)
        pygame_surf_dessin = pygame_module.surface.Surface(taille_surf_dessin)
        injec.core.set_realpygame_screen(pgscreen)

    result = upscaling[chosen_mode]
    injec.core.set_virtual_screen(pygame_surf_dessin, upscaling[chosen_mode])

    # CAN keep this implicit...
    # if upscaling[chosen_mode] is not None:
    #    print('upscaling x{}'.format(upscaling[chosen_mode]))

    # - BLOC qui etait censé sexecuter que si pas en Web ctx... {{
    if caption is None:
        caption = f'untitled demo, uses KENGI ver {registered_vernum}'
    pygame_module.display.set_caption(caption)

    injec.event.create_manager()
    game_ticker = injec.event.GameTicker(maxfps)
    # - }}

    return result  # can be None, if no upscaling applied


def retrieve_game_ctrl():
    global engine_is_init, game_ticker, _multistate, _stack_based_ctrl
    assert engine_is_init

    if _multistate:
        return _stack_based_ctrl
    else:
        return game_ticker


def tag_multistate(allstates, glvars_pymodule, providedst_classes=None):
    global game_ticker, _stack_based_ctrl, _multistate

    _multistate = True
    _stack_based_ctrl = injec.event.StackBasedGameCtrl(
        game_ticker, allstates, glvars_pymodule, providedst_classes
    )


def get_manager():
    return injec.gl_unique_manager


def old_cleanup():
    global engine_is_init
    assert engine_is_init
    injec.event.gl_unique_manager.hard_reset()
    injec.event.CogObj.reset_class_state()

    injec.pygame.mixer.quit()
    injec.pygame.quit()

    engine_is_init = False


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
