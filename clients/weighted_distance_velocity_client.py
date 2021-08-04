from conf import CLIENT_TIMEOUT, TIMER_DELAY
from clients.triggers.trigger import Trigger
from clients.triggers.structs import Position, Velocity, TriggerShape
from clients.utils import _get_normalized_velocity
from tminterface.client import Client
from tminterface.interface import TMInterface
from tminterface.structs import BFPhase, BFEvaluationInfo, BFEvaluationResponse, BFEvaluationDecision


# The minimum improvement for a run to be qualified
MIN_DISTANCE_IMPROVEMENT = 0.0001
MIN_VELOCITY_IMPROVEMENT = 0.001

# Value close to 1 will prefer Distance over Velocity
# Value close to 0 will prefer Velocity over Distance
WEIGHT = 0.95

# Index for distance/velocity in our saved runs
DISTANCE_INDEX = 0
VELOCITY_INDEX = 1


class WeightedDistanceVelocity(Client):
    def __init__(self, trigger_shape: TriggerShape):
        super().__init__()
        self.reference_time = None
        self.reference_distance = None
        self.reference_velocity = None
        self.run_time = None
        self.initial_trigger = False
        self.init_done = False
        self.trigger = Trigger(shape=trigger_shape)
        self.reference_run = None
        self.current_run = None
        self.iterations = None

    def on_registered(self, tm_interface: TMInterface) -> None:
        print(f"Registered to {tm_interface.server_name}")
        tm_interface.set_timeout(CLIENT_TIMEOUT)

    def on_simulation_begin(self, tm_interface):
        """Reset the variables for a new simulation"""
        self.run_time = tm_interface.get_event_buffer().events_duration
        self.reference_time = self.run_time
        self.initial_trigger = False
        self.init_done = False
        self.reference_run = [0 for _ in range(0, self.run_time + 10, 10)]
        self.current_run = [0 for _ in range(0, self.run_time + 10, 10)]
        self.iterations = 0

    def _init_phase(self, tm_interface: TMInterface, current_time: int) -> BFEvaluationResponse:
        """ During init phase, we save the current run as a referenced run
        If the run crosses the trigger, we save those information as well.
        This function will be called for every improvements.
        """
        response = BFEvaluationResponse()
        response.decision = BFEvaluationDecision.CONTINUE

        # Don't save counter
        if current_time < 0:
            return response

        simulation_state = tm_interface.get_simulation_state()

        car_pos = Position(*simulation_state.get_position())
        car_distance = self.trigger.get_distance(car_pos)
        car_vel = _get_normalized_velocity(Velocity(*simulation_state.get_velocity()))

        # Save all couple distance to trigger / velocity at any state as reference
        self.reference_run[current_time // 10] = car_distance, car_vel

        # We have to setup the base run for future variation as the server does not replay unchanged states
        self.current_run[current_time // 10] = car_distance, car_vel

        # If we collide with the trigger, we have to save the time one frame before
        if not self.initial_trigger and self.trigger.has_colided(car_pos):
            self.initial_trigger = True
            self.reference_time = current_time - 10
            if not self.init_done:
                print(
                    f"Hit trigger during initial phase with time: {self.reference_time},"
                    f" dist: {self.reference_run[(current_time - 10) // 10][DISTANCE_INDEX]} "
                    f"and vel: {self.reference_run[(current_time - 10) // 10][VELOCITY_INDEX]}"
                )
                self.init_done = True

        return response

    def on_bruteforce_evaluate(self, tm_interface: TMInterface, info: BFEvaluationInfo) -> BFEvaluationResponse:
        """There is 2 main phases:
        At BFPhase.INITIAL, we save the run as a reference run.
        At BFPhase.SEARCH, we save a copy of the current run, and check if the run is better or not.
        """
        current_time = info.time - TIMER_DELAY

        # First run / New best run
        if info.phase == BFPhase.INITIAL:
            return self._init_phase(tm_interface, current_time)

        response = BFEvaluationResponse()
        response.decision = BFEvaluationDecision.CONTINUE

        if info.phase != BFPhase.SEARCH:
            return response

        if current_time > self.run_time:
            response.decision = BFEvaluationDecision.REJECT
            self.increase_iterations()
            return response

        simulation_state = tm_interface.get_simulation_state()

        car_pos = Position(*simulation_state.get_position())
        car_distance = self.trigger.get_distance(car_pos)
        car_vel = _get_normalized_velocity(Velocity(*simulation_state.get_velocity()))

        # Save the current variations
        self.current_run[current_time // 10] = car_distance, car_vel

        # If we collide with the trigger, it has to be before or at the current reference time, once
        if self.trigger.has_colided(car_pos):
            if current_time - 10 > self.reference_time:
                saved_frame = self.current_run[self.reference_time // 10]
                reference_frame = self.reference_run[self.reference_time // 10]
            else:
                saved_frame = self.current_run[(current_time - 10) // 10]
                reference_frame = self.reference_run[(current_time - 10) // 10]
            distance_improvement = reference_frame[DISTANCE_INDEX] - saved_frame[DISTANCE_INDEX]
            velocity_improvement = saved_frame[VELOCITY_INDEX] - reference_frame[VELOCITY_INDEX]

            distance_score = (
                0
                if -MIN_DISTANCE_IMPROVEMENT < distance_improvement < MIN_DISTANCE_IMPROVEMENT
                else distance_improvement * WEIGHT * 100
            )
            velocity_score = (
                0
                if -MIN_VELOCITY_IMPROVEMENT < velocity_improvement < MIN_VELOCITY_IMPROVEMENT
                else velocity_improvement * (1 - WEIGHT) * 100
            )

            if distance_score + velocity_score <= 0:
                response.decision = BFEvaluationDecision.REJECT
                self.increase_iterations()
                return response

            print(
                f"New trigger at {current_time - 10} with distance "
                f"{saved_frame[DISTANCE_INDEX]:.6f} and velocity {saved_frame[VELOCITY_INDEX]:.6f} "
                f"iterations: {self.iterations}."
            )
            response.decision = BFEvaluationDecision.ACCEPT
            self.initial_trigger = False
            self.increase_iterations()
            return response
        response.decision = BFEvaluationDecision.DO_NOTHING
        return response

    def increase_iterations(self):
        self.iterations += 1
        if self.iterations % 100 == 0:
            print(f"{self.iterations} iterations.")

