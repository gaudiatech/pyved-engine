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
class AvStyle:
    style: int = 0  # 0, 1, 2 are ok


@component
class DirMobileBehavior:
    angle: float = 0.0
    thrust: float = 0.0
    delta_angle: float = 0.0


@component
class Health:
    max_hp: int
    hp: int = None


@component
class Perks:
    li_perks: Iterable[str]


# ----------------------------------------
#  ENTITIES
# ----------------------------------------
@entity
class Player(DirMobileBehavior, AvStyle, Health, MobPosition, Perks):  # WARNING: order matters a lot!
    # You have to use the REVERSE order:
    # compos that hav only default values <<-- mixed compos <<-- compos that have only un-initialized values
    pass
