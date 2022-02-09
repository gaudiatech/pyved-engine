
"""
to be set externally when engine.init is called
"""
runs_in_web = None
pygame = None
pygame_gfxdraw = None


# OTHER vars
CONST_SCR_SIZE = (960, 540)
screen = None  # ref to Surface

#  exec in the regular ctx
# ---------------------------------
_real_pygamescreen = None

canvas_emuvram = None
ctx_emuvram = None

canvas_rendering = None
ctx_rendering = None

_stored_upscaling = 1


def register_upscaling(upscaling_val):
    global _stored_upscaling
    _stored_upscaling = int(upscaling_val)


def get_upscaling():
    global _stored_upscaling
    return _stored_upscaling


def conv_to_vscreen(x, y):
    global _stored_upscaling
    return int(x/_stored_upscaling), int(y/_stored_upscaling)


def set_canvas_rendering(jsobj):
    global canvas_rendering, ctx_rendering
    canvas_rendering = jsobj
    # ctx_rendering = jsobj.getContext('2d')


def set_canvas_emu_vram(jsobj):
    global canvas_emuvram, ctx_emuvram
    canvas_emuvram = jsobj
    ctx_emuvram = jsobj.getContext('2d')


def set_realpygame_screen(ref_surf):
    global _real_pygamescreen
    _real_pygamescreen = ref_surf


def set_virtual_screen(ref_surface, upscaling):
    global screen, _stored_upscaling

    screen = ref_surface
    if upscaling is not None:
        _stored_upscaling = int(upscaling)

    # if _stored_upscaling > 1:
    #     if runs_in_web:
    #         ctx = canvas_rendering.getContext('2d')
    #         ctx.imageSmoothingEnabled = False
    #         ctx.scale(_stored_upscaling, _stored_upscaling)
    #         print('upscaling applied on canvas...')
