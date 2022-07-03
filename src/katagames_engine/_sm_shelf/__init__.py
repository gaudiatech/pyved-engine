"""
all elements in this sub-modules are imported directly

via Injector
(dependency injection manager)

use the:

  import katagames_sdk.engine as kataen
  kataen.*

syntax
"""

# N.b need to import so setup.py can detect all files

from . import core
from . import console
from . import gfx
from . import terrain
from . import rogue
from . import tabletop
