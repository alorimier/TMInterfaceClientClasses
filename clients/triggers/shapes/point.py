import math
from dataclasses import dataclass

from clients.triggers.structs import TriggerShape, Position


@dataclass
class TriggerPoint(TriggerShape):
    x: float
    y: float
    z: float

    def has_colided(self, car_pos) -> bool:
        raise NotImplementedError("There's no collision with a point.")

    def get_distance(self, car_pos: Position) -> float:
        super().get_distance(car_pos)
        vec_x = car_pos.x - self.x
        vec_y = car_pos.y - self.y
        vec_z = car_pos.z - self.z

        return math.sqrt(vec_x * vec_x + vec_y * vec_y + vec_z * vec_z)
