import math
from dataclasses import dataclass

from clients.triggers.structs import TriggerShape, Position


@dataclass
class TriggerCube(TriggerShape):
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float

    def has_colided(self, car_pos) -> bool:
        super().get_distance(car_pos)
        if self.x2 >= car_pos.x >= self.x1 and self.y2 >= car_pos.y >= self.y1 and self.z2 >= car_pos.z >= self.z1:
            return True
        return False

    def get_distance(self, car_pos: Position) -> float:
        super().get_distance(car_pos)

        if self.x1 <= car_pos.x <= self.x2:
            if self.y1 <= car_pos.y <= self.y2:
                return min(abs(self.z1 - car_pos.z), abs(car_pos.z - self.z2))
            if self.z1 <= car_pos.z <= self.z2:
                return min(abs(self.y1 - car_pos.y), abs(car_pos.y - self.y2))
            dy = min(abs(self.y1 - car_pos.y), abs(car_pos.y - self.y2))
            dz = min(abs(self.z1 - car_pos.z), abs(car_pos.z - self.z2))
            return math.sqrt(dy * dy + dz * dz)
        if self.y1 <= car_pos.y <= self.y2:
            if self.z1 <= car_pos.z <= self.z2:
                return min(abs(self.x1 - car_pos.x), abs(car_pos.x - self.x2))
            dz = min(abs(self.z1 - car_pos.z), abs(car_pos.z - self.z2))
            dx = min(abs(self.x1 - car_pos.x), abs(car_pos.x - self.x2))
            return math.sqrt(dx * dx + dz * dz)
        if self.z1 <= car_pos.z <= self.z2:
            dx = min(abs(self.x1 - car_pos.x), abs(car_pos.x - self.x2))
            dy = min(abs(self.y1 - car_pos.y), abs(car_pos.y - self.y2))
            return math.sqrt(dx * dx + dy * dy)
        dx = min(abs(self.x1 - car_pos.x), abs(car_pos.x - self.x2))
        dy = min(abs(self.y1 - car_pos.y), abs(car_pos.y - self.y2))
        dz = min(abs(self.z1 - car_pos.z), abs(car_pos.z - self.z2))
        return math.sqrt(dx * dx + dy * dy + dz * dz)
