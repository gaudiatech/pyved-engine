# - avoid rel import for brython
# from ...foundation import shared
# from .... import engine as kataen

from .. import _hub as injec
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
    if upscaling is not None:
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
            pyg.transform.scale(shared.screen, shared.CONST_SCR_SIZE, realscreen)
    pyg.display.update()


def get_screen():
    return shared.screen


def get_disp_size():
    # display
    return 960, 540


# deprecated /!\
def runs_in_web():
    return shared.RUNS_IN_WEB_CTX


# -----------------------------------
# -<>- public procedures: utils -<>-
# -----------------------------------
def proj_to_vscreen(org_screen_pos):
    return conv_to_vscreen(*org_screen_pos)


# -----------------------------------
#  can PROXY some things if it's really universal needs
#   => should be prefixed by .core
# --
def declare_states(mapping_enum_classes, mod_glvars=None):
    all_states = list(mapping_enum_classes.keys())
    injec.legacy.tag_multistate(
        all_states, mod_glvars, False, providedst_classes=mapping_enum_classes
    )


def init(gfc_mode='hd'):
    injec.legacy.legacyinit(gfc_mode)
    # _new_state(-1)


def get_game_ctrl():
    return injec.legacy.retrieve_game_ctrl()


def get_manager():  # saves some time
    return injec.event.EventManager.instance()


def cleanup():
    injec.legacy.old_cleanup()
