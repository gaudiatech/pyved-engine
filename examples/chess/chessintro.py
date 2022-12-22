import chdefs
import katagames_engine as kengi


kengi.bootstrap_e()


# - alias
pygame = kengi.pygame
EngineEvTypes = kengi.EngineEvTypes


def proc_start():
    kengi.get_ev_manager().post(EngineEvTypes.StatePush, state_ident=chdefs.ChessGstates.Chessmatch)
    print('apres start ->', chdefs.pltype1, chdefs.pltype2)


class IntroCompo(kengi.EvListener):
    """
    main component for this game state
    """
    def _update_playertypes(self):
        chdefs.pltype1 = chdefs.OMEGA_PL_TYPES[self.idx_pl1]
        chdefs.pltype2 = chdefs.OMEGA_PL_TYPES[self.idx_pl2]
        self.pltypes_labels[0].text = chdefs.pltype1
        self.pltypes_labels[1].text = chdefs.pltype2

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

        self.pltypes_labels = [
            kengi.gui.Label((115, 145), 'unkno type p1', color='darkblue'),
            kengi.gui.Label((115, 205), 'unkno type p2', color='darkblue'),
        ]
        self._update_playertypes()

        # - v: buttons
        def rotatepl1():
            self.idx_pl1 = (self.idx_pl1+1) % len(chdefs.OMEGA_PL_TYPES)
            self._update_playertypes()

        def rotatepl2():
            self.idx_pl2 = (self.idx_pl2+1) % len(chdefs.OMEGA_PL_TYPES)
            self._update_playertypes()

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
        for lab in self.pltypes_labels:
            lab.draw()

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
