from .defs import EngineEvTypes, to_camelcase
from .interfaces import BaseKenBackend
from .. import _hub
from .. import vars


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
        4: 'lB',
        5: 'rB',
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
        self.pyg_jm = None  # model for joystickS
        self.lstick_val_cache = [0.0, 0.0]
        self.rstick_val_cache = [0.0, 0.0]

    def joystick_init(self, idj):
        self.pyg_jm = self._pygame_mod.joystick.Joystick(idj)
        self.pyg_jm.init()

    def joystick_info(self, idj):
        return self.pyg_jm.get_name()

    def joystick_count(self):
        return self._pygame_mod.joystick.get_count()

    def _map_etype2kengi(self, alien_etype):
        if alien_etype not in self.__class__.static_mapping:
            if self.debug_mode:  # notify that there's no conversion
                print('[no conversion] pygame etype=', alien_etype)  # alien_etype.dict)
        else:
            if self.joypad_events_bounds[0] <= alien_etype <= self.joypad_events_bounds[1]:
                pass
                # for convenient gamepad support, we map pygame JOY* in a more specialized way (xbox360 pad support) 2/2
                # else:
            return self.__class__.static_mapping[alien_etype]

    def fetch_kengi_events(self):
        cst_joyaxismotion = 1536
        cst_joyballmotion = 1537
        cst_hatmotion = 1538
        cst_joydown = 1539
        cst_joyup = 1540

        raw_pyg_events = self._pygame_mod.event.get()
        del self._ev_storage[:]

        for pyev in raw_pyg_events:
            # for convenient gamepad support, we will
            # map pygame JOY* in a specialized way (xbox360 pad support)
            if pyev.type == cst_joyaxismotion:
                if pyev.axis in (0, 1):
                    self.lstick_val_cache[pyev.axis] = pyev.value
                    self._ev_storage.append(
                        (EngineEvTypes.Stickmotion, {'side': 'left', 'pos': tuple(self.lstick_val_cache)})
                    )
                elif pyev.axis in (2, 3):
                    self.rstick_val_cache[-2+pyev.axis] = pyev.value
                    self._ev_storage.append(
                        (EngineEvTypes.Stickmotion, {'side': 'right', 'pos': tuple(self.rstick_val_cache)})
                    )
                elif pyev.axis == 4:
                    self._ev_storage.append(
                        (EngineEvTypes.Gamepaddown, {'button': 'lTrigger', 'value': pyev.value})
                    )
                elif pyev.axis == 5:
                    self._ev_storage.append(
                        (EngineEvTypes.Gamepaddown, {'button': 'rTrigger', 'value': pyev.value})
                    )

            elif pyev.type == cst_joyballmotion:
                # ignore
                pass

            elif pyev.type == cst_hatmotion:  # joy Dpad has been activated
                # <Event(1538-JoyHatMotion {'joy': 0, 'instance_id': 0, 'hat': 0, 'value': (0, 0)})>
                setattr(pyev, 'dir', self.dpad_mapping[pyev.value])  # east, west, etc.
                tmp = list(pyev.value)
                if tmp[1] != 0:
                    tmp[1] *= -1
                pyev.value = pyev.dict['value'] = tuple(tmp)
                self._ev_storage.append((self._map_etype2kengi(pyev.type), pyev.dict))

            elif pyev.type == cst_joydown or pyev.type == cst_joyup:  # joybtdown/joybtup
                pyev.button = self.joy_bt_map[pyev.button]  # change name of the button
                setattr(pyev, 'value', int(pyev.type == cst_joydown))
                self._ev_storage.append((self._map_etype2kengi(pyev.type), pyev.dict))

            else:
                k_event = (self._map_etype2kengi(pyev.type), pyev.dict)
                self._ev_storage.append(k_event)

        return self._ev_storage


def build_primalbackend(pbe_identifier, libbundle_ver=None):
    """
    :param pbe_identifier: str
    values accepted -> to make a valid func. call you would either pass '' or 'web'
    :param libbundle_ver: str
    """
    if pbe_identifier == '':  # default
        return PygameKenBackend()

    elif pbe_identifier == 'web':
        if libbundle_ver is None:
            if vars.weblib_sig is None or len(vars.weblib_sig)<1:
                raise ValueError('since you use the web backend you HAVE TO specify libbundle_ver !!')
            else:
                adhoc_ver = vars.weblib_sig
        else:
            adhoc_ver = libbundle_ver

        # its assumed that (injector entry 'web_pbackend')
        # => (module==web_pbackend.py & cls==WebPbackend)
        # for example
        modulename = 'web_pbackend'
        BackendAdhocClass = getattr(_hub.kengi_inj[modulename], to_camelcase(modulename))
        print('   *inside build_primalbackend*  adhoc class is ', BackendAdhocClass)
        return BackendAdhocClass(adhoc_ver)  # web backends need to ver. info. in great details!
    else:
        raise ValueError(f'value "{pbe_identifier}" isnt supported, when calling (engine)build_primalbackend !')
