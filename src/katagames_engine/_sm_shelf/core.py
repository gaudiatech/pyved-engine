from collections import defaultdict

from .. import _hub as injec
from ..__version__ import ENGI_VERSION
from ..foundation import defs as engi_defs
from ..foundation import shared


def register_upscaling(upscaling_val):
    shared.stored_upscaling = int(upscaling_val)


def get_upscaling():
    return shared.stored_upscaling


def conv_to_vscreen(x, y):
    ups = shared.stored_upscaling
    return int(x/ups), int(y/ups)


def set_canvas_rendering(jsobj):
    shared.canvas_rendering = jsobj


def set_canvas_emu_vram(jsobj):
    shared.canvas_emuvram = jsobj
    shared.ctx_emuvram = jsobj.getContext('2d')


def set_realpygame_screen(ref_surf):
    shared.real_pygamescreen = ref_surf


def set_virtual_screen(ref_surface, upscaling):
    shared.screen = ref_surface
    if upscaling != 1.0:
        shared.stored_upscaling = int(upscaling)


# --------- avant ca ct gfx_updater.py
def display_update():
    pyg = injec.pygame
    if not shared.RUNS_IN_WEB_CTX:
        # ---------------
        #  runs in ctx Win/Mac
        # ---------------
        realscreen = pyg.display.get_surface()
        if 1 == get_upscaling():
            realscreen.blit(shared.screen, (0, 0))
        else:
            pyg.transform.scale(shared.screen, engi_defs.STD_SCR_SIZE, realscreen)
    pyg.display.update()


def get_screen():
    return shared.screen


# - deprecated
# it's confusing! When upscaling is used its unclear what size is returned here,
# better avoid this function...
# def get_disp_size():
#     return shared.CONST_SCR_SIZE


# - deprecated /!\
# def runs_in_web():
#    return shared.RUNS_IN_WEB_CTX


# -----------------------------------
# -<>- public procedures: utils -<>-
# -----------------------------------
def proj_to_vscreen(org_screen_pos):
    return conv_to_vscreen(*org_screen_pos)


def declare_states(gsdefinition, assoc_gscode_cls, mod_glvars=None):
    global _multistate, state_stack, _stack_based_ctrl, _loaded_states

    # verif
    # for ke in assoc_code_gs_cls.keys():
    #     if ke in _loaded_states.keys():
    #         print('[Warning] gamestate code {} was already taken. Overriding state(risky)...'.format(ke))
    #         del _loaded_states[ke]
    #
    # for ke, cls in assoc_code_gs_cls.items():
    #     print(cls)
    #     _loaded_states[ke] = cls(ke)
    x = gsdefinition
    y = mod_glvars

    _multistate = True
    state_stack = injec.struct.Stack()
    _stack_based_ctrl = injec.event.StackBasedGameCtrl(
        game_ticker, x, y, assoc_gscode_cls
    )


def get_game_ctrl():
    global init2_done, _multistate, _stack_based_ctrl, game_ticker
    assert init2_done
    if _multistate:
        print('retour stack based ctrl ***')
        return _stack_based_ctrl
    else:
        return game_ticker


def get_manager():  # saves some time
    return injec.event.EventManager.instance()


# -------------------------------- below the line you find
# # ----------------------------  legacy code, maybe I can simplify this more

init2_done = False
headless_mode = False
game_ticker = None
SCR_SIZE = None  # virtual scr size
_multistate = False
_stack_based_ctrl = None
_loaded_states = dict()
_curr_state = None
state_stack = None


# TODO
# - deprecated, I should find a better way to init directly from katagames_engine.implem
def init_e2(chosen_mode, caption, maxfps, screen_dim=None):
    global init2_done, game_ticker, SCR_SIZE

    if init2_done:
        raise ValueError('legacyinit called while engine_is_init==True')

    pygame_module = injec.pygame

    pygame_module.init()
    if not shared.RUNS_IN_WEB_CTX:
        pygame_module.mixer.init()
    else:
        pygame_module.time.do_fake_init()

    init2_done = True

    if chosen_mode not in engi_defs.OMEGA_DISP_CODES:
        raise ValueError(f'display requested is {chosen_mode}, but this isnt a valid disp. mode in Kengi!')
    else:
        bw, bh = engi_defs.STD_SCR_SIZE
        drawspace_dim = {
            engi_defs.HD_DISP: (bw, bh),
            engi_defs.OLD_SCHOOL_DISP: (bw // 2, bh // 2),
            engi_defs.SUPER_RETRO_DISP: (bw // 3, bh // 3),
            engi_defs.CUSTOM_DISP: screen_dim
        }
        upscaling = defaultdict(lambda: 1.0)
        upscaling[engi_defs.SUPER_RETRO_DISP] = 3.0
        upscaling[engi_defs.OLD_SCHOOL_DISP] = 2.0

        if chosen_mode == engi_defs.CUSTOM_DISP and (screen_dim is None):
            raise ValueError('custom mode for gfx, but no screen_dim found!')

        taille_surf_dessin = drawspace_dim[chosen_mode]

        if shared.RUNS_IN_WEB_CTX:
            print('call display set_mode with arg: ')
            print(taille_surf_dessin)
            pygame_surf_dessin = pygame_module.display.set_mode(taille_surf_dessin)
        else:
            if chosen_mode == engi_defs.CUSTOM_DISP:
                pgscreen = pygame_module.display.set_mode(taille_surf_dessin)
            else:
                pgscreen = pygame_module.display.set_mode(engi_defs.STD_SCR_SIZE)
            pygame_surf_dessin = pygame_module.surface.Surface(taille_surf_dessin)
            injec.core.set_realpygame_screen(pgscreen)

        result = upscaling[chosen_mode]
        set_virtual_screen(pygame_surf_dessin, upscaling[chosen_mode])

        # CAN keep this implicit...
        # if upscaling[chosen_mode] is not None:
        #    print('upscaling x{}'.format(upscaling[chosen_mode]))

        # - BLOC qui etait censé sexecuter que si pas en Web ctx... {{
        if caption is None:
            caption = f'untitled demo, uses KENGI ver {ENGI_VERSION}'
        pygame_module.display.set_caption(caption)

        injec.event.create_manager()
        game_ticker = injec.event.GameTicker(maxfps)
        # - }}
        return result  # can be None, if no upscaling applied


def _new_state(gs_code):
    """
    manually change the state.
    /!\ this is probably deprecated as it overrides what the StContainer is doing...
    """
    global _curr_state, state_stack, _loaded_states

    print('new state call')
    print(gs_code)
    print(str(_loaded_states))

    if _curr_state:
        _curr_state.release()
        state_stack.pop()

    state_stack.push(gs_code)
    _curr_state = _loaded_states[gs_code]
    _curr_state.enter()
