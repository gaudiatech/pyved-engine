from . import _hub
from .foundation import defs


_cached_eff_pygame = None
_vsurface = None
_vsurface_required = True

special_flip = 0  # flag, set it to 1 when using web ctx
screen = None
stored_upscaling = 1

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
    global _cached_eff_pygame, _vsurface_required, _vsurface
    if _cached_eff_pygame is None:
        _cached_eff_pygame = _hub.pygame
    if _vsurface_required:
        # TODO
        pass

    if special_flip:  # flag can be off if the extra blit/transform has to disabled (web ctx)
        _cached_eff_pygame.display.update()
    else:
        pyg = _cached_eff_pygame
        realscreen = pyg.display.get_surface()
        if 1 == stored_upscaling:
            realscreen.blit(screen, (0, 0))
        else:
            pyg.transform.scale(screen, defs.STD_SCR_SIZE, realscreen)
        pyg.display.update()
