import time
from abc import ABCMeta, abstractmethod

from . import _hub
from . import vars
from ._pyv_implem import close_game, init, get_ev_manager
from .compo.vscreen import flip as _flip_screen
from .core.events import EngineEvTypes


__all__ = [
    'ConfigStorage',
    'Objectifier',
    'GameTpl'
]


# may be deprecated, due to pyv.vars
# TODO investigate?
class ConfigStorage:
    MAXFPS = 45
    SCR_SIZE = (None, None)
    UPSCALING = None  # not defined, yet


class Objectifier:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class GameTpl(metaclass=ABCMeta):
    """
    the "no name" game template class. It allows to define your game in a quick way,
    by redefining one or several methods: enter, update, exit
    """
    INFO_STOP_MSG = 'kengi.GameTpl->the loop() call has ended.'
    ERR_LOCK_MSG = 'kengi.GameTpl.loop called while SAFETY_LOCK is on!'
    SAFETY_LOCK = False  # can be set to True from outside, if you don't want a game to call .loop()

    def __init__(self):
        self.gameover = False
        self.nxt_game = 'niobepolis'
        self._manager = None
        self.clock = None

    @abstractmethod
    def get_video_mode(self):
        raise NotImplementedError

    def list_game_events(self):
        """
        :return: all specific/custom game events
        """
        return None

    def enter(self, vms=None):
        """
        Careful if you redefine this:
        one *HAS TO*
         - init video
         - set the gameticker
         - set the _manager attribute (bind the ev manager to self._manager)
         - call self._manager.setup(...) with args
        """
        init(self.get_video_mode())
        self.clock = vars.game_ticker  # bind
        self._manager = get_ev_manager()
        self._manager.setup(self.list_game_events())
        self._manager.post(EngineEvTypes.Gamestart)  # pushed to notify that we have really started playing

    def update(self, infot):
        pyg = _hub.kengi_inj['pygame']
        pk = pyg.key.get_pressed()
        if pk[pyg.K_ESCAPE]:
            self.gameover = True
            return 2, self.nxt_game

        self._manager.post(EngineEvTypes.Update, curr_t=infot)
        self._manager.post(EngineEvTypes.Paint, screen=vars.screen)
        self._manager.update()
        _flip_screen()
        self.clock.tick(vars.max_fps)

    def exit(self, vms=None):
        close_game()

    def loop(self):
        """
        its forbidden to call .loop() in the web ctx, but its convenient in the local ctx
        if one wants to test a program without using the Kata VM
        :return:
        """
        # lock mechanism, for extra safety so we never call .loop() in the web ctx
        if self.SAFETY_LOCK:
            raise ValueError(self.ERR_LOCK_MSG)

        # use enter, update, exit to handle the global "run game logic"
        self.enter()

        while not self.gameover:
            infot = time.time()
            self.update(infot)
        self.exit()
        print(self.INFO_STOP_MSG)
