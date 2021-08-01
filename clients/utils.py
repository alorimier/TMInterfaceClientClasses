import math

from clients.triggers.structs import Velocity


def _get_normalized_velocity(car_vel: Velocity) -> float:
    return math.sqrt(car_vel.x * car_vel.x + car_vel.y * car_vel.y + car_vel.z * car_vel.z)
