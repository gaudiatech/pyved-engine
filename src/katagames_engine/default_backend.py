import pygame

from .core import EngineEvTypes, BaseKenBackend


class PygameKenBackend(BaseKenBackend):
    static_mapping = {
        256: EngineEvTypes.Quit,  # pygame.QUIT is 256
        32787: EngineEvTypes.Quit,  # for pygame2.0.1+ we also have 32787 -> pygame.WINDOWCLOSE
        771: EngineEvTypes.BasicTextinput,  # pygame.TEXTINPUT

        32768: EngineEvTypes.Activation,  # pygame.ACTIVEEVENT, has "gain" and "state" attributes
        32783: EngineEvTypes.FocusGained,  # pygame.WINDOWFOCUSGAINED
        32784: EngineEvTypes.FocusLost,  # pygame.WINDOWFOCUSLOST

        pygame.KEYDOWN: EngineEvTypes.Keydown,
        pygame.KEYUP: EngineEvTypes.Keyup,
        pygame.MOUSEMOTION: EngineEvTypes.Mousemotion,
        pygame.MOUSEBUTTONDOWN: EngineEvTypes.Mousedown,
        pygame.MOUSEBUTTONUP: EngineEvTypes.Mouseup,
    }

    def pull_events(self):
        return pygame.event.get()

    def map_etype2kengi(self, alien_etype):
        if alien_etype not in self.__class__.static_mapping:
            # no conversion
            print('[no conversion] pygame etype=', alien_etype)  # alien_etype.dict)
        else:
            return self.__class__.static_mapping[alien_etype]
