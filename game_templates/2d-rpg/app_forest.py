import katagames_engine as kengi


BaseGameState = kengi.BaseGameState
EventReceiver = kengi.EvListener
EngineEvTypes = kengi.EngineEvTypes
pygame = kengi.pygame


class ForestView(EventReceiver):
    def __init__(self):
        super().__init__()
        self._bg_color = 'darkgreen'
        ft = pygame.font.Font(None, 19)
        self.img = ft.render('press ESCAPE to go back to the prev. state', True, (0, 0, 0))
        self.img_pos = (200, 180)

    # override
    def on_paint(self, ev):
        ev.screen.fill(self._bg_color)
        ev.screen.blit(self.img, self.img_pos)


class ForestCtrl(EventReceiver):
    def __init__(self):
        super().__init__()

    # override
    def on_keydown(self, ev):
        if ev.key == pygame.K_ESCAPE:
            self.pev(EngineEvTypes.StatePop)
            print('event sent: StatePop')


class ForestState(BaseGameState):
    def __init__(self, gs_id):
        super().__init__(gs_id)
        self.m = self.v = self.c = None

    def enter(self):
        print('entering ForestState...')
        self.v = ForestView()
        self.v.turn_on()
        self.c = ForestCtrl()
        self.c.turn_on()

    def release(self):
        print('releasing ForestState!')
        self.c.turn_off()
        self.c = None
        self.v.turn_off()
        self.v = None
