import katagames_engine as kengi
from chdefs import ChessGstates
import chdefs

kengi.bootstrap_e()


# - alias
pygame = kengi.pygame
EngineEvTypes = kengi.EngineEvTypes


class DummyV(kengi.EvListener):
    def __init__(self, go):
        super().__init__()
        self.gameobj = go

    def turn_on(self):
        super().turn_on()
        print('press RETURN to start a match')

    def on_paint(self, ev):
        ev.screen.fill('antiquewhite3')

    def on_keydown(self, ev):
        if ev.key == pygame.K_RETURN:
            # print('pev --> StatePush, state_ident=', ChessGstates.Chessmatch)
            self.pev(EngineEvTypes.StatePush, state_ident=ChessGstates.Chessmatch)
        elif ev.key == pygame.K_ESCAPE:
            self.gameobj.gameover = True
        else:
            print('[DummyV] unhandled key is pressed')


class ChessintroState(kengi.BaseGameState):
    # bind state_id to class is done automatically by kengi (part 1 /2)
    def __init__(self, ident):
        super().__init__(ident)
        self.d = None

    def enter(self):
        self.d = DummyV(chdefs.ref_game_obj)
        self.d.turn_on()

    def release(self):
        self.d.turn_off()

    def pause(self):
        self.d.turn_off()
        print('intro paused')

    def resume(self):
        self.d.turn_on()
        print('intro resumed')
