

_adhoc_pygame = None
_runs_in_web_ctx = None
_cached_gfxdraw = None

def get_module():
    global _adhoc_pygame, _runs_in_web_ctx

    if _adhoc_pygame is None:

        if _runs_in_web_ctx is None:
            _runs_in_web_ctx = '__BRYTHON__' in globals()

        if _runs_in_web_ctx:
            import katagames_sdk.pygame_emu as _pygame_emu
            _adhoc_pygame = _pygame_emu
        else:
            import pygame as _pygame
            _adhoc_pygame = _pygame

    return _adhoc_pygame


def import_gfxdraw():
    global _runs_in_web_ctx, _cached_gfxdraw
    if _cached_gfxdraw is None:
        if _runs_in_web_ctx:
            import katagames_sdk.pygame_emu.gfxdraw as _gfxdraw
            _cached_gfxdraw = _gfxdraw
        else:
            import pygame.gfxdraw as _gfxd
            _cached_gfxdraw = _gfxd
    return _cached_gfxdraw


def test_web_context():
    global _runs_in_web_ctx
    if _runs_in_web_ctx is None:
        _runs_in_web_ctx = '__BRYTHON__' in globals()
    return _runs_in_web_ctx
