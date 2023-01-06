import katagames_engine as kengi


BaseGameState = kengi.BaseGameState
EventReceiver = kengi.EvListener
EngineEvTypes = kengi.EngineEvTypes
pygame = kengi.pygame


class WorldView(EventReceiver):

    def __init__(self):
        super().__init__()
        self._bg_color = 'cyan'
        ft = pygame.font.Font(None, 19)
        self.img = ft.render('press ESCAPE to go back to the prev. state', True, (0, 0, 0))
        self.img_pos = (200, 180)

    # override
    def on_event(self, ev):
        if ev.type == EngineEvTypes.Paint:
            ev.screen.fill(self._bg_color)
            ev.screen.blit(self.img, self.img_pos)


class WorldCtrl(EventReceiver):

    def __init__(self):
        super().__init__()

    # override
    def on_event(self, ev):
        if ev.type == EngineEvTypes.Keydown and ev.key == pygame.K_ESCAPE:
            self.pev(EngineEvTypes.StatePop)
            print('sent POP')


class OverworldState(BaseGameState):
    def __init__(self, gs_id):
        super().__init__(gs_id)
        self.m = self.v = self.c = None

    def enter(self):
        print('you begin your adventure!')
        self.v = WorldView()
        self.v.turn_on()
        self.c = WorldCtrl()
        self.c.turn_on()

    def release(self):
        print('you came back home.')
        self.c.turn_off()
        self.c = None
        self.v.turn_off()
        self.v = None
