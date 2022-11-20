import time

import katagames_engine as kengi
from UthModel import UthModel


# alias def.
pygame = kengi.pygame
EngineEvTypes = kengi.event2.EngineEvTypes
ReceiverObj = kengi.event2.EvListener


class UthCtrl(ReceiverObj):
    AUTOPLAY_DELAY = 0.8  # sec

    def __init__(self, model):
        super().__init__()
        self._mod = model
        self._last_t = None
        self.elapsed = 0

    def on_update(self, ev):
        if self._mod.autoplay_flag:
            elapsed = time.time() - self._last_t
            if elapsed > self.AUTOPLAY_DELAY:
                self._mod.evolve_state()
                self._last_t = time.time()

    def on_end_round_requested(self, ev):
        self._mod.autoplay_flag = True
        self._mod.evolve_state()
        self._last_t = time.time()

    def on_keydown(self, ev):
        if ev.key == pygame.K_ESCAPE:
            self.pev(EngineEvTypes.Gameover)

        if not self._mod.autoplay_flag:
            # backspace will be used to CHECK / FOLD
            if ev.key == pygame.K_BACKSPACE:
                self._mod.input_check()

            # enter will be used to select the regular BET option, x3, x2 or x1 depends on the stage
            elif ev.key == pygame.K_RETURN:
                # ignore non-valid case
                self._mod.input_bet(0)

            # case: at the beginning of the game the player can select the MEGA-BET x4 lets use space for that
            # we'll also use space to begin the game. State transition: init -> discov
            elif ev.key == pygame.K_SPACE:
                if self._mod.stage == UthModel.INIT_ST_CODE:
                    return
                if self._mod.stage != UthModel.DISCOV_ST_CODE:
                    return
                self._mod.input_bet(1)
