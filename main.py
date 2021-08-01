import time

from clients.weighted_distance_velocity_client import WeightedDistanceVelocity
from conf import trigger_shape
from tminterface.interface import TMInterface


def main():
    client = WeightedDistanceVelocity(trigger_shape)

    tm_interface = TMInterface()
    tm_interface.register(client)

    while tm_interface.running:
        time.sleep(0)


if __name__ == "__main__":
    exit(main())
