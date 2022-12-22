import katagames_engine as kengi
from chdefs import ChessGstates
import chdefs


# - alias
pygame = kengi.pygame
EngineEvTypes = kengi.EngineEvTypes


class DummyV(kengi.EvListener):
    def __init__(self, go):
        super().__init__()
        self.gameobj = go

    def turn_on(self):
        super().turn_on()
        print('press RETURN to start the game')

    def on_paint(self, ev):
        ev.screen.fill('pink')

    def on_keydown(self, ev):
        if ev.key == pygame.K_RETURN:
            self.pev(EngineEvTypes.StateChange, state_ident=ChessGstates.Chessmatch)
        elif ev.key == pygame.K_ESCAPE:
            self.gameobj.gameover = True
        else:
            print('unknown key pressed [[DummyV cls]]')


class ChessintroMode(kengi.BaseGameState):
    # bind state_id to class is done automatically by kengi (part 1 /2)

    def enter(self):
        self.d = DummyV(chdefs.ref_game_obj)
        self.d.turn_on()

    def release(self):
        self.d.turn_off()
