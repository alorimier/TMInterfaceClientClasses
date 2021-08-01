from clients.triggers.structs import Position, Mode, TriggerShape


class Trigger:
    def __init__(self, shape: TriggerShape, min_improvment: float = 0.001, mode: Mode = Mode.POSITION):
        self.shape = shape
        self.min_improvment = min_improvment
        self.mode = mode

    def has_colided(self, car_pos: Position) -> bool:
        return self.shape.has_colided(car_pos)

    def get_distance(self, car_pos: Position) -> float:
        return self.shape.get_distance(car_pos)
