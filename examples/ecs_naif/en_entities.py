from typing import Iterable

from katagames_engine import component, entity


@component
class Position:
    x: int
    y: int


@component
class Speed:
    vx: float
    vy: float


@component
class Health:
    max_hp: int
    hp: int


@component
class Perks:
    li_perks: Iterable[str]


# --- def entités ---
@entity
class Player(Health, Perks, Position, Speed):
    pass
