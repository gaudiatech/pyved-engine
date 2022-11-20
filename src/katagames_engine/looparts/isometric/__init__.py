"""
Barebones isometric_map handling for an isometric RPG. For game-specific data,
either subclass the Scene or just declare whatever extra bits are needed.
"""

from .IsometricMapViewer import IsometricMapViewer
from .IsometricMapViewer0 import IsometricMapViewer0
# from . import extras
from . import model
from .extras import IsometricMapQuarterCursor as IsoCursor


def set_tiled_version(vernum):
    if float(vernum) < 1.9:
        model.info_type_obj = 'type'
        print('*LEGACY isometric model ON*')
