from clients.triggers.shapes.point import TriggerPoint
from conf import CLIENT_TIMEOUT, TIMER_DELAY
from clients.triggers.trigger import Trigger
from clients.triggers.structs import Position, Velocity, TriggerShape
from clients.utils import _get_normalized_velocity
from tminterface.client import Client
from tminterface.interface import TMInterface
from tminterface.structs import BFPhase, BFEvaluationInfo, BFEvaluationResponse, BFEvaluationDecision


MAX_TIME = 38000
MIN_DISTANCE = 0.001


class ClosestToPoint(Client):
    def __init__(self, trigger_point: TriggerPoint):
        super().__init__()
        self.run_time = None
        self.trigger = trigger_point
        self.shortest_distance = None
        self.is_better_run = None
        self.init_done = None
        self.iterations = None
        self.best_time = None

    def on_registered(self, tm_interface: TMInterface) -> None:
        print(f"Registered to {tm_interface.server_name}")
        tm_interface.set_timeout(CLIENT_TIMEOUT)

    def on_simulation_begin(self, tm_interface):
        """Reset the variables for a new simulation"""
        self.run_time = tm_interface.get_event_buffer().events_duration
        self.is_better_run = False
        self.init_done = False
        self.iterations = 0
        self.best_time = self.run_time
        self.shortest_distance = None

    def _init_phase(self, tm_interface: TMInterface, info: BFEvaluationInfo, current_time: int) -> BFEvaluationResponse:
        """Save the closest distance."""
        response = BFEvaluationResponse()
        response.decision = BFEvaluationDecision.CONTINUE

        if self.init_done:
            return response

        # Don't check before min time
        if current_time < info.inputs_min_time:
            return response

        simulation_state = tm_interface.get_simulation_state()

        car_pos = Position(*simulation_state.get_position())
        car_distance = self.trigger.get_distance(car_pos)

        if not self.shortest_distance or self.shortest_distance - car_distance > MIN_DISTANCE:
            self.shortest_distance = car_distance
            self.best_time = current_time

        if current_time == MAX_TIME and not self.init_done:
            self.init_done = True
            print(f"Best distance during init phase: {self.shortest_distance} at {self.best_time}.")

        return response

    def on_bruteforce_evaluate(self, tm_interface: TMInterface, info: BFEvaluationInfo) -> BFEvaluationResponse:
        current_time = info.time - TIMER_DELAY

        # First run / New best run
        if info.phase == BFPhase.INITIAL:
            return self._init_phase(tm_interface, info, current_time)

        response = BFEvaluationResponse()
        response.decision = BFEvaluationDecision.DO_NOTHING

        if current_time < info.inputs_min_time:
            return response

        if info.phase != BFPhase.SEARCH:
            print("Wrong phase")
            return response

        simulation_state = tm_interface.get_simulation_state()

        car_pos = Position(*simulation_state.get_position())
        car_distance = self.trigger.get_distance(car_pos)

        if self.shortest_distance - car_distance > MIN_DISTANCE or not self.shortest_distance:
            self.shortest_distance = car_distance
            self.best_time = current_time
            self.is_better_run = True

        if current_time == MAX_TIME:
            if self.is_better_run:
                print(f"Found better distance: {self.shortest_distance} at {current_time} in {self.iterations} iterations.")
                self.increase_iterations()
                response.decision = BFEvaluationDecision.ACCEPT
                self.is_better_run = False
            else:
                self.increase_iterations()
                print("Rejected")
                response.decision = BFEvaluationDecision.REJECT
        return response

    def increase_iterations(self):
        self.iterations += 1
        if self.iterations % 100 == 0:
            print(f"{self.iterations} iterations.")

