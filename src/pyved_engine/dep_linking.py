"""
this is a temporary file in order to extract .pygame
from ._hub

We get plenty of circular dependencies,
 because pyv submodules often rely on pygame.

But these submodules are supposed to be indexed by the _hub python module
"""


pygame = None
