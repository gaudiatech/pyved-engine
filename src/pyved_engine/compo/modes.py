from ..Singleton import Singleton
from ..util import drawtext


@Singleton
class GameModeMger:
    def __init__(self):
        self.menus = dict()
        self._mode = self.menu = None

    @property
    def mode(self):
        return self._mode

    def set_curr_mode(self, mode_name):
        self._mode = mode_name
        self.menu = self.menus[mode_name]

    def register(self, dictobj):
        self.menus.update(dictobj)

    def switch_mode(self, mode, reset=False):
        if mode in self.menus:
            self._mode = mode
            self.menu = self.menus[self.mode]
            if reset:
                self.menu.__init__(self.menu.name)

    def update(self, events):
        self.menu.update(events)

    def draw(self, surf):
        self.menu.draw(surf)


class BaseGameMode:
    """
    Base signature for all menus
    """

    def __init__(self, name='menu'):
        self._manager = GameModeMger.instance()
        self.name = name

    def update(self, events):  # list[pygame.event.Event]):
        pass

    def draw(self, surf):
        surf.blit(drawtext(self.name, aliased=True), (50, 50))
