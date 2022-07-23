from .. import vscreen as shared


_curr_state = None
_loaded_states = dict()
init2_done = False
state_stack = None


def conv_to_vscreen(x, y):
    dw, dh = shared.screen.get_size()
    ups = int(960/dw)
    return int(x / ups), int(y / ups)


def set_canvas_rendering(jsobj):
    shared.canvas_rendering = jsobj


def set_canvas_emu_vram(jsobj):
    shared.canvas_emuvram = jsobj
    shared.ctx_emuvram = jsobj.getContext('2d')


def set_realpygame_screen(ref_surf):
    if shared.real_pygamescreen:
        print('warning: set_realpygame_scneen called a 2nd time. Ignoring request')
        return
    shared.real_pygamescreen = ref_surf


def set_virtual_screen(ref_surface):
    shared.screen = ref_surface
    shared.screen_rank += 1


def get_screen():
    return shared.screen


def proj_to_vscreen(org_screen_pos):
    return conv_to_vscreen(*org_screen_pos)
