# import time
# from abc import ABCMeta, abstractmethod
# from . import _hub
# from . import vars
# from ._pyv_implem import close_game, init, get_ev_manager, declare_game_states
# from .compo.vscreen import flip as _flip_screen
# from .core.events import EngineEvTypes


__all__ = [
    'ConfigStorage',
    'Objectifier'
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
