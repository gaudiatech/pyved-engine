"""
replica of the pygame legacy event sys
"""
from . import _hub


def get():
    return _hub.pygame.event.get()


def pressed_keys():
    return _hub.pygame.key.get_pressed()


def __getattr__(name):  # expose(->like forwarding) all pygame key codes & pygame constants
    if name == 'QUIT':
        return _hub.pygame.QUIT
    try:
        return getattr(_hub.pygame.key, name)
    except AttributeError:
        return getattr(_hub.pygame, name)
