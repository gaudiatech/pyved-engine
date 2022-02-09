from abc import ABCMeta, abstractmethod


class BaseGameState(metaclass=ABCMeta):

    def __init__(self, state_ident, state_name):
        self.__state_ident = state_ident
        self.__state_name = state_name

    def get_id(self):
        return self.__state_ident

    def get_name(self):
        return self.__state_name

    @abstractmethod
    def enter(self):
        pass

    @abstractmethod
    def release(self):
        pass

    def resume(self):
        print(self.__class__.__name__)
        raise AssertionError('not meant to be resumed')

    def pause(self):
        print(self.__class__.__name__)
        raise AssertionError('not meant to be paused')
