"""
surcouche à pygame permettant d'utiliser l'ancien système d'évents,
sans rendre fort le lien à pygame & sans dépendance forte à l'API de pygame
"""
from .. import _hub


def get():  # direct access to the pygame event system
    return _hub.pygame.event.get()


def pressed_keys():  # direct access to the pygame key.get_pressed()
    return _hub.pygame.key.get_pressed()


def __getattr__(keyname):
    try:
        return getattr(_hub.pygame, keyname)

    except AttributeError:
        print('cannot find the specified key:', keyname)
