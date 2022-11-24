from .defs import EngineEvTypes, to_camelcase
from .interfaces import BaseKenBackend
from .. import _hub


class PygameKenBackend(BaseKenBackend):
    """
    Important architecture change:
    instead of:

                   /-->pygame_API(full)- -+---->pygameSDL
                 /                       /
               /                       /
    kengiCore +----> pygame_API(subset) -----> pygameEm


    Tom has chosen:                     /----> web pbackend -----> pygameEm+JS
                                       /
    pygame_API(subset) ---> kengiCore +
                                       \
                                        \\--> default pbackend ----> pygameSDL

    Main benefits are:

     * expliciting the subset
     * no more flawed emulation-related errors, if smth runs in local (Imagine that Bob is calling kengi.pygame.*)
       it should never crash in web ctx
     * from now on, our own low-level API can differ a lot from pygame's API. Our low-level API is freely defined
       in the abstract backend/ backend interface
     * less code coupling. If we ever drop the pygame support/if pygame_API receives heavy patches,
     it won't become a disaster
    """
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

        # gamepad support
        1536: EngineEvTypes.Stickmotion,  # JOYAXISMOTION:  self.joy[event.joy].axis[event.axis] = event.value
        1537: None,  # JOYBALLMOTION:  self.joy[event.joy].ball[event.ball] = event.rel
        1538: EngineEvTypes.GamepadDir,  # JOYHATMOTION:  self.joy[event.joy].hat[event.hat] = event.value
        1539: EngineEvTypes.Gamepaddown,  # JOYBUTTONDOWN: self.joy[event.joy].button[event.button] = 1
        1540: EngineEvTypes.Gamepadup,  # JOYBUTTONUP:  self.joy[event.joy].button[event.button] = 0
    }
    joypad_events_bounds = [1536, 1540]

    joy_bt_map = {
        0: 'A',
        1: 'B',
        2: 'X',
        3: 'Y',
        4: 'LbKey',
        5: 'RbKey',
        6: 'Back',
        7: 'Start'
    }
    dpad_mapping = {
        (0, 0): None,
        (0, 1): 'north',
        (1, 0): 'east',
        (0, -1): 'south',
        (-1, 0): 'west',
        (1, 1): 'north-east',
        (-1, 1): 'north-west',
        (-1, -1): 'south-west',
        (1, -1): 'south-east'
    }

    def __init__(self):
        import pygame as _genuine_pyg
        _hub.kengi_inj.set('pygame', _genuine_pyg)
        self._pygame_mod = _hub.kengi_inj['pygame']
        self.debug_mode = False
        self._ev_storage = list()
        self.jm = None  # model for joystickS

    def joystick_count(self):
        return self._pygame_mod.joystick.get_count()

    def joystick_init(self, idj):
        self.jm = self._pygame_mod.joystick.Joystick(idj)
        self.jm.init()

    def joystick_info(self, idj):
        return self.jm.get_name()

    def pull_events(self):
        del self._ev_storage[:]
        self._ev_storage.extend(self._pygame_mod.event.get())

        # for convenient gamepad support, we map pygame JOY* in a specialized way (xbox360 pad support) 1/2
        for e in self._ev_storage:
            if e.type == 1539 or e.type == 1540:  # joybtdown/joybtup
                e.button = self.joy_bt_map[e.button]
            elif e.type == 1538:  # joy Dpad has been activated
                e.dir = self.dpad_mapping[e.value]
            elif e.type == 1536:  # JOYAXISMOTION (0,1) ->joy L; (2,3)->joyR;  4 & 5->triggers Left & Right
                # pyg has values in [-1,1]
                pass

        return self._ev_storage

    def map_etype2kengi(self, alien_etype):
        if alien_etype not in self.__class__.static_mapping:
            if self.debug_mode:  # notify that there's no conversion
                print('[no conversion] pygame etype=', alien_etype)  # alien_etype.dict)
        else:
            if self.joypad_events_bounds[0] <= alien_etype <= self.joypad_events_bounds[1]:
                pass
                # for convenient gamepad support, we map pygame JOY* in a more specialized way (xbox360 pad support) 2/2
                # else:
            return self.__class__.static_mapping[alien_etype]


def build_primalbackend(pbe_identifier: str):
    if pbe_identifier == '':  # default
        return PygameKenBackend()

    else:
        # it's assumed that (injector entry 'web_pbackend')
        #  => (module==web_pbackend.py & cls==WebPbackend)
        # for example
        inj_e, cls_name = pbe_identifier+'_pbackend', to_camelcase(pbe_identifier+'_pbackend')
        return getattr(_hub.kengi_inj[inj_e], cls_name)()
