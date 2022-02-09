from .Singleton import Singleton


_CONST_SDK_VER_STRING = '0.0.7'


@Singleton
class PygproxyBringer:

    def __init__(self):
        from .EmuPygproxy import EmuPygproxy
        from .GenuinePygproxy import GenuinePygproxy

        self._runs_in_web = '__BRYTHON__' in globals()
        if self._runs_in_web:
            self._provider = EmuPygproxy()
        else:
            self._provider = GenuinePygproxy()

        self._cached_pygame = None
        self._cached_gfxdraw = None

    @property
    def framework_version(self):
        return _CONST_SDK_VER_STRING

    @property
    def web_enabled(self):
        return self._runs_in_web

    def pygame(self):
        if self._cached_pygame is None:
            self._cached_pygame = self._provider.provide_pygame()
        return self._cached_pygame

    def pygame_gfxdraw(self):
        if self._cached_gfxdraw is None:
            self._cached_gfxdraw = self._provider.provide_gfxdraw()
        return self._cached_gfxdraw
