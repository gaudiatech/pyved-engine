from .defs import EngineEvTypes, to_camelcase
from .interfaces import BaseKenBackend
from .. import _hub


def build_primalbackend(pbe_identifier: str = ''):
    if pbe_identifier == '':  # default
        return PygameKenBackend()
    else:
        # injector e: 'web_pbackend',
        # cls name WebPbackend, for example
        inj_e = pbe_identifier + '_pbackend'
        cls_name = to_camelcase(inj_e)
        return getattr(_hub.kengi_inj[inj_e], cls_name)()


class PygameKenBackend(BaseKenBackend):
    static_mapping = {
        256: EngineEvTypes.Quit,  # pygame.QUIT is 256
        32787: EngineEvTypes.Quit,  # for pygame2.0.1+ we also have 32787 -> pygame.WINDOWCLOSE
        771: EngineEvTypes.BasicTextinput,  # pygame.TEXTINPUT

        32768: EngineEvTypes.Activation,  # pygame.ACTIVEEVENT, has "gain" and "state" attributes
        32783: EngineEvTypes.FocusGained,  # pygame.WINDOWFOCUSGAINED
        32784: EngineEvTypes.FocusLost,  # pygame.WINDOWFOCUSLOST

        768: EngineEvTypes.Keydown,  # pygame.KEYDOWN
        769: EngineEvTypes.Keyup,  # pygame.KEYUP
        1024: EngineEvTypes.Mousemotion,  # pygame.MOUSEMOTION
        1025: EngineEvTypes.Mousedown,  # pygame.MOUSEBUTTONDOWN
        1026: EngineEvTypes.Mouseup,  # pygame.MOUSEBUTTONUP
    }

    def __init__(self):
        self._pygame_mod = _hub.kengi_inj['pygame']
        self.debug_mode = False

    def pull_events(self):
        return self._pygame_mod.event.get()

    def map_etype2kengi(self, alien_etype):
        if alien_etype not in self.__class__.static_mapping:
            if self.debug_mode:  # notify that there's no conversion
                print('[no conversion] pygame etype=', alien_etype)  # alien_etype.dict)
        else:
            return self.__class__.static_mapping[alien_etype]
