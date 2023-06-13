from typing import Iterable

from pyved_engine import component, entity


# ----------------------------------------
#  COMPONENTS
# ----------------------------------------
@component
class MobPosition:
    x: int
    y: int


@component
class DirMobileBehavior:
    angle: float
    thrust: float
    delta_angle: float = 0


@component
class Health:
    hp: int
    max_hp: int


@component
class Perks:
    li_perks: Iterable[str]


# ----------------------------------------
#  ENTITIES
# ----------------------------------------
@entity
class Player(DirMobileBehavior, MobPosition, Health, Perks):
    pass
