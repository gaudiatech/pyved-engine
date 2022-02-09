from abc import abstractmethod, ABCMeta


class BasePygprox(metaclass=ABCMeta):

    @abstractmethod
    def provide_pygame(self):
        raise NotImplementedError

    @abstractmethod
    def provide_gfxdraw(self):
        raise NotImplementedError
