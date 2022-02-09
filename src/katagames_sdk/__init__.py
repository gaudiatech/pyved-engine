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
                    ->alpha_pyg
    ----------------------
"""
from . import engine
from .alpha_pyg.PygproxyBringer import PygproxyBringer as _BringerCls

from ._deco import web_animate, web_entry_point  # import decorators that can be used to create links for the web ctx
from . import _deco as _web_ctx_decorators  # retrieve what has been linked thx to decorators


version = VERSION = _BringerCls.instance().framework_version


def import_pygame():
    return _BringerCls.instance().pygame()


def import_pygame_gfxdraw():
    return _BringerCls.instance().pygame_gfxdraw()


def retrv_web_entry_point():
    return _web_ctx_decorators.linkto_web_entry_point


def retrv_web_animate():
    return _web_ctx_decorators.linkto_web_animate
