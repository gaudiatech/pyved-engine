from abc import ABCMeta, abstractmethod
from collections import deque


__all__ = [
    'BaseGameState',
    'Objectifier',
    'CircularBuffer'
]


class BaseGameState(metaclass=ABCMeta):

    def __init__(self, state_ident):
        self.__state_ident = state_ident
        self.__state_name = self.__class__.__name__

    @abstractmethod
    def enter(self):
        pass

    def get_id(self):
        return self.__state_ident

    def get_name(self):
        return self.__state_name

    def pause(self):
        print(self.__class__.__name__)
        raise AssertionError('not meant to be paused')

    @abstractmethod
    def release(self):
        pass

    def resume(self):
        print(self.__class__.__name__)
        raise AssertionError('not meant to be resumed')


# may be deprecated, due to pyv.vars
# TODO investigate?
# class ConfigStorage:
#     MAXFPS = 45
#     SCR_SIZE = (None, None)
#     UPSCALING = None  # not defined, yet


class Objectifier:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class CircularBuffer:

    def __init__(self, gmax_len=128):
        """
        Initialize the CircularBuffer with a gmax_len if given. Default size is 128
        """
        self.deque_obj = deque(maxlen=gmax_len)

    def __str__(self):
        """Return a formatted string representation of this CircularBuffer."""
        items = ['{!r}'.format(item) for item in self.deque_obj]
        return '[' + ', '.join(items) + ']'

    def get_size(self):
        return len(self.deque_obj)

    def is_empty(self):
        """Return True if the head of the CircularBuffer is equal to the tail,
        otherwise return False"""
        return len(self.deque_obj) == 0

    def is_full(self):
        """Return True if the tail of the CircularBuffer is one before the head,
        otherwise return False"""
        return len(self.deque_obj) == self.deque_obj.maxlen

    def enqueue(self, item):
        """Insert an item at the back of the CircularBuffer
        Runtime: O(1) Space: O(1)"""
        self.deque_obj.append(item)

    def dequeue(self):
        """Return the item at the front of the Circular Buffer and remove it
        Runtime: O(1) Space: O(1)"""
        return self.deque_obj.popleft()

    def front(self):
        """Return the item at the front of the CircularBuffer
        Runtime: O(1) Space: O(1)"""
        if len(self.deque_obj):
            return self.deque_obj[len(self.deque_obj) - 1]
        raise IndexError('circular buffer is currently empty!')
