import chdefs
import katagames_engine as kengi
from chdefs import ChessGstates


kengi.bootstrap_e()


# - alias
pygame = kengi.pygame
EngineEvTypes = kengi.EngineEvTypes


def proc_start():
    kengi.get_ev_manager().post(EngineEvTypes.StatePush, state_ident=ChessGstates.Chessmatch)


class IntroCompo(kengi.EvListener):
    """
    main component for this game state
    """
    def __init__(self):
        super().__init__()

        # model
        self.idx_pl1 = 0
        self.idx_pl2 = 0

        # - v: labels
        # current sig is:
        # (position, text, txtsize=35, color=None, anchoring=ANCHOR_LEFT, debugmode=False)
        sw = kengi.get_surface().get_width()
        self.title = kengi.gui.Label((sw//2, 100), 'The game of chess', anchoring=kengi.gui.ANCHOR_CENTER)
        self.title.textsize = 122
        self.title.color = 'brown'

        # - v: buttons
        def rotatepl1():
            self.idx_pl1 = (self.idx_pl1+1) % 4
            print(self.idx_pl1)

        def rotatepl2():
            self.idx_pl2 = (self.idx_pl2+1) % 4
            print(self.idx_pl2)

        self.buttons = [
            kengi.gui.Button((128, 256), (200, 50), 'Start Chessmatch'),
            kengi.gui.Button((128 + 200 + 25, 140), (60, 60), ' > '),
            kengi.gui.Button((128 - 25 - 60, 140), (60, 60), ' < '),
            kengi.gui.Button((128+200+25, 200), (60, 60), ' > '),
            kengi.gui.Button((128-25-60, 200), (60, 60), ' < '),
        ]

        self.buttons[0].callback = proc_start
        self.buttons[1].callback = rotatepl1
        self.buttons[3].callback = rotatepl2

    def turn_on(self):
        super().turn_on()
        print('press RETURN to start a match')

    def on_paint(self, ev):
        ev.screen.fill('antiquewhite3')
        self.title.draw()
        for b in self.buttons:
            ev.screen.blit(b.image, b.rect.topleft)

    def on_mousedown(self, ev):
        for b in self.buttons:
            if b.rect.collidepoint(ev.pos) and b.callback:
                b.callback()

    def on_keydown(self, ev):
        if ev.key == pygame.K_ESCAPE:
            chdefs.ref_game_obj.gameover = True
        elif ev.key == pygame.K_RETURN:
            proc_start()
        else:
            print('[DummyV] unhandled key is pressed')


class ChessintroState(kengi.BaseGameState):
    def __init__(self, ident):
        super().__init__(ident)
        self.icompo = None

    def enter(self):
        self.icompo = IntroCompo()
        self.icompo.turn_on()

    def resume(self):
        self.icompo.turn_on()

    def release(self):
        self.icompo.turn_off()

    def pause(self):
        self.icompo.turn_off()
