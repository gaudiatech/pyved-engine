import time

import katagames_engine as kengi
from UthModel import MyEvTypes


# - aliases
EngineEvTypes = kengi.event.EngineEvTypes
pygame = kengi.pygame
ReceiverObj = kengi.event.EventReceiver


class UthCtrl(ReceiverObj):
    AUTOPLAY_DELAY = 1.333  # sec

    def __init__(self, model):
        super().__init__()
        self._mod = model
        self._last_t = None
        self.elapsed = 0

    def proc_event(self, ev, source):

        if ev.type == EngineEvTypes.LOGICUPDATE:
            if self._mod.autoplay_flag:
                elapsed = time.time() - self._last_t
                if elapsed > self.AUTOPLAY_DELAY:
                    self._mod.evolve_state()
                    self._last_t = time.time()

        elif ev.type == MyEvTypes.PlayerBets:
            self._mod.autoplay_flag = True
            self._mod.evolve_state()
            self._last_t = time.time()

        elif ev.type == pygame.KEYDOWN:  # -------- manage keyboard
            if ev.key == pygame.K_ESCAPE:
                self.pev(EngineEvTypes.GAMEENDS)

            if not self._mod.autoplay_flag:
                # backspace will be used to CHECK / FOLD
                if ev.key == pygame.K_BACKSPACE:
                    self._mod.input_choice(0)

                # enter will be used to select the regular BET option, x3, x2 or x1 depends on the stage
                elif ev.key == pygame.K_RETURN:
                    self._mod.input_choice(1)

                # case: at the beginning of the game the player can select the MEGA-BET x4 lets use space for that
                # we'll also use space to begin the game. State transition: init -> discov
                elif ev.key == pygame.K_SPACE:
                    self._mod.input_choice(2)
