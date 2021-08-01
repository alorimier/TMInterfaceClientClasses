from dataclasses import dataclass
from enum import Enum


@dataclass
class Coord:
    x: float
    y: float
    z: float


@dataclass
class Position(Coord):
    pass


@dataclass
class Velocity(Coord):
    pass


class Mode(Enum):
    POSITION = 0
    VELOCITY = 1


class TriggerShape:
    def has_colided(self, car_pos: Position) -> bool:
        pass

    def get_distance(self, car_pos: Position) -> float:
        pass
