import katagames_sdk.engine as kataen
from defs4 import GameStates
from katagames_sdk.engine import BaseGameState
from katagames_sdk.engine import EngineEvTypes, EventReceiver


pygame = kataen.import_pygame()


class MenuScreenView(EventReceiver):

    def __init__(self):
        super().__init__(self)
        self._bg_color = (255, 50, 60)  # red, green, blue format
        ft = pygame.font.Font(None, 19)
        self.img = ft.render('press mouse button to change state', True, (0, 0, 0))
        self.img_pos = (200, 180)

    # override
    def proc_event(self, ev, source=None):
        if ev.type == EngineEvTypes.PAINT:
            ev.screen.fill(self._bg_color)
            ev.screen.blit(self.img, self.img_pos)


class MenuScreenCtrl(EventReceiver):

    def __init__(self):
        super().__init__()

    # override
    def proc_event(self, ev, source=None):

        if ev.type == pygame.MOUSEBUTTONDOWN:
            print('pushing the ClickChallg state onto the stack...')
            self.pev(EngineEvTypes.PUSHSTATE, state_ident=GameStates.ClickChallg)


class MenuScreenState(BaseGameState):
    def __init__(self, gs_id, name):
        super().__init__(gs_id, name)
        self.m = self.v = self.c = None

    def enter(self):
        print('entering MenuScreen state...')
        self.v = MenuScreenView()
        self.v.turn_on()
        self.c = MenuScreenCtrl()
        self.c.turn_on()

    def release(self):
        print('RELEASING MenuScreenState !')
        self.c.turn_off()
        self.c = None
        self.v.turn_off()
        self.v = None

    # override
    def pause(self):
        print('MenuScreen state is paused.')
        self.c.turn_off()
        self.v.turn_off()

    # override
    def resume(self):
        print('MenuScreen state is resumed.')
        self.v.turn_on()
        self.c.turn_on()
