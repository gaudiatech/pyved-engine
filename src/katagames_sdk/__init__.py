"""
KataSDK (c) Gaudia Tech Inc. 2018-2022

author: thomas iwaszko

to learn more:
www.github.com/wkta
www.github.com/gaudiatech

----------------------
SDK structure overview
----------------------
ext_*
    .dep
        ->engine
            .dep
                ->pygame

------
GOALS:
------

 * to provide a multiplatform support in several flavors:
   (1) with the kata engine
   (2) bare pygame
"""

from . import _deco as _web_ctx_decorators  # retrieve what has been linked thx to decorators
from ._deco import web_animate, web_entry_point  # import decorators that can be used to create links for the web ctx

# retro-compat:
from . import engine


version = VERSION = '0.0.8'


def multiplat_support():
    from . import engine as enmo

    # web ctx support
    # IMPORTANT: hacking needs to be done before the engine.init(...) call!
    if '__BRYTHON__' in globals():
        print('............web ctx.............')
        # need to build a bridge to the backend... Inject parameter
        from .pygame_emu import bridge
        from .backe_py_coating import BackendFactory
        bridge.gfx_backend = BackendFactory().create('pixelate')
        # - why hacking the engine? To enable multiplatform compat.
        from . import pygame_emu

        # secondary task: {STARTS HERE}
        # create link to fix pygame_emu.overlay
        # (a deprecated way of doing, but dunno how to replace it for now)
        from .engine.foundation import events as events_feat
        pygame_emu.overlay.link_to_own_event_sm(events_feat)
        # {ENDS HERE}

        enmo.submodule_hacking('pygame', pygame_emu)

    return enmo


def retrv_web_entry_point():
    return _web_ctx_decorators.linkto_web_entry_point


def retrv_web_animate():
    return _web_ctx_decorators.linkto_web_animate
