from .. import _hub
from ..foundation import defs as engi_defs
from ..foundation import shared


_curr_state = None
_loaded_states = dict()

init2_done = False
state_stack = None


def conv_to_vscreen(x, y):
    ups = shared.stored_upscaling
    return int(x / ups), int(y / ups)


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


def display_update():
    pyg = _hub.pygame
    realscreen = pyg.display.get_surface()

    if not shared.special_flip:  # flag can be off if the extra blit/transform has to disabled (web ctx)
        if 1 == shared.stored_upscaling:
            realscreen.blit(shared.screen, (0, 0))
        else:
            pyg.transform.scale(shared.screen, engi_defs.STD_SCR_SIZE, realscreen)

    pyg.display.update()


def get_screen():
    return shared.screen


def proj_to_vscreen(org_screen_pos):
    return conv_to_vscreen(*org_screen_pos)


# def _new_state(gs_code):
#     """
#     manually change the state.
#     /! this is probably deprecated as it overrides what the StContainer is doing...
#     """
#     global _curr_state, state_stack, _loaded_states
#
#     print('new state call')
#     print(gs_code)
#     print(str(_loaded_states))
#
#     if _curr_state:
#         _curr_state.release()
#         state_stack.pop()
#
#     state_stack.push(gs_code)
#     _curr_state = _loaded_states[gs_code]
#     _curr_state.enter()
