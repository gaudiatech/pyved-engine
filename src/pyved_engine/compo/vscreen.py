from ..foundation import defs
from .. import vars


_vsurface = None
_vsurface_required = True

cached_pygame_mod = None  # init from outside when one calls kengi.bootstrap_e
special_flip = 0  # flag, set it to 1 when using web ctx
stored_upscaling = 1
defacto_upscaling = None

# hopefully i will be able to simplify this:
ctx_emuvram = None
canvas_emuvram = None
canvas_rendering = None
real_pygamescreen = None
screen_rank = 1  # so we can detect whenever its required to update the var in the PAINT engine event


def set_upscaling(new_upscal_val):
    global stored_upscaling, _vsurface_required
    if stored_upscaling is not None:
        if int(stored_upscaling) != new_upscal_val:
            stored_upscaling = int(new_upscal_val)
            _vsurface_required = True


def flip():
    global _vsurface_required, _vsurface
    if _vsurface_required:
        # TODO
        pass

    if not special_flip:  # flag can be off if the extra blit/transform has to disabled (web ctx)
        realscreen = cached_pygame_mod.display.get_surface()
        if 1 == stored_upscaling:
            realscreen.blit(vars.screen, (0, 0))
        else:
            cached_pygame_mod.transform.scale(vars.screen, defs.STD_SCR_SIZE, realscreen)

    cached_pygame_mod.display.update()


# ------------------------------------
#   old code
# ------------------------------------
_curr_state = None
_loaded_states = dict()
init2_done = False
state_stack = None


def conv_to_vscreen(x, y):
    return int(x / defacto_upscaling), int(y / defacto_upscaling)


# def set_canvas_rendering(jsobj):
#     shared.canvas_rendering = jsobj
#
#
# def set_canvas_emu_vram(jsobj):
#     shared.canvas_emuvram = jsobj
#     shared.ctx_emuvram = jsobj.getContext('2d')


def set_realpygame_screen(ref_surf):
    global real_pygamescreen
    if real_pygamescreen:
        print('warning: set_realpygame_scneen called a 2nd time. Ignoring request')
        return
    real_pygamescreen = ref_surf


def set_virtual_screen(ref_surface):
    global screen_rank, defacto_upscaling
    vars.screen = ref_surface
    w = vars.screen.get_size()[0]
    defacto_upscaling = 960/w
    screen_rank += 1


def proj_to_vscreen(org_screen_pos):
    # TODO repair
    # return conv_to_vscreen(*org_screen_pos)
    return org_screen_pos
