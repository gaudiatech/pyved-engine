import re
from . import _hub
from pathlib import Path


FONT = 'consolas'


def _font(size):
    return _hub.kengi_inj['pygame'].font.SysFont(FONT, size)


def camel_case_format(string_ac_underscores):
    words = [word.capitalize() for word in string_ac_underscores.split('_')]
    return "".join(words)


def drawtext(msg, size=50, color=(255, 255, 255), aliased=False):
    return _font(size).render(msg, aliased, color)


def underscore_format(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def path_to_img_infos(filepath):
    """
    :param filepath: for example /users/tom/machin.png
    :return: both the future image name(identifier) that is "machin" and a filename thing to load: "machin.png"
    """
    pobj = Path(filepath)
    return pobj.stem, pobj.name
