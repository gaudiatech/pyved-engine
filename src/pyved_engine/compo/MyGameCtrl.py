from .. import vars
from ..compo.vscreen import flip as _flip_screen
from ..core import events


class MyGameCtrl(events.EvListener):
    """
    WARNING! This demo cannot be used within the Web ctx,
    because of the blocking loop.
    We should need a way around this, see
    """
    def __init__(self):
        super().__init__()
        self._clock = vars.clock
        self.gameover = False

    def on_gameover(self, ev):
        self.gameover = True

    def loop(self):
        # right now, in cas of a multistate game you would use another
        # class. That is: pyv.state_management.StateStackCtrl
        # we should unify this otherwise the engine would remain quite dirty
        # TODO unification

        # forced line? Used to enter the initial state "enter" method
        # self.pev(events.EngineEvTypes.Gamestart)
        while True:
            self.pev(events.EngineEvTypes.Update)
            self.pev(events.EngineEvTypes.Paint, screen=vars.screen)
            self._manager.update()
            _flip_screen()
            self._clock.tick(vars.max_fps)
            if self.gameover or vars.gameover:
                return  # break the game loop on purpose
