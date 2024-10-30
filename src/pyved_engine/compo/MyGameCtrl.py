from ..core import events
from .. import vars
from ..compo.vscreen import flip as _flip_screen


class MyGameCtrl(events.EvListener):

    def __init__(self):
        super().__init__()
        self._clock = vars.clock
        self.gameover = False

    def on_gameover(self, ev):
        self.gameover = True

    def loop(self):
        # if state_management.multistate_flag:  # force this, otherwise the 1st state enter method isnt called
        #     self.pev(events.EngineEvTypes.Gamestart)
        while not self.gameover:
            self.pev(events.EngineEvTypes.Update)
            self.pev(events.EngineEvTypes.Paint, screen=vars.screen)
            self._manager.update()
            _flip_screen()
            self._clock.tick(vars.max_fps)
