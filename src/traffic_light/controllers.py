from __future__ import annotations

from dataclasses import dataclass

from traffic_light.config import PhaseName

PHASE_LANES: dict[PhaseName, tuple[str, str]] = {
    "north_south": ("north", "south"),
    "east_west": ("east", "west"),
}


def other_phase(phase: PhaseName) -> PhaseName:
    return "east_west" if phase == "north_south" else "north_south"


@dataclass
class ControllerState:
    now: float
    current_phase: PhaseName
    phase_started_at: float
    queues: dict[str, int]


class BaseController:
    name = "base"

    def choose_phase(self, state: ControllerState) -> PhaseName:
        raise NotImplementedError


@dataclass
class FixedTimeController(BaseController):
    phase_duration_seconds: int = 35
    name: str = "fixed"

    def choose_phase(self, state: ControllerState) -> PhaseName:
        elapsed = state.now - state.phase_started_at
        if elapsed >= self.phase_duration_seconds:
            return other_phase(state.current_phase)
        return state.current_phase


@dataclass
class ActuatedController(BaseController):
    min_green_seconds: int = 15
    decision_interval_seconds: int = 10
    name: str = "actuated"

    def choose_phase(self, state: ControllerState) -> PhaseName:
        elapsed = state.now - state.phase_started_at
        if elapsed < self.min_green_seconds or int(state.now) % self.decision_interval_seconds:
            return state.current_phase

        current_pressure = sum(state.queues[lane] for lane in PHASE_LANES[state.current_phase])
        other = other_phase(state.current_phase)
        other_pressure = sum(state.queues[lane] for lane in PHASE_LANES[other])
        return other if other_pressure > current_pressure + 1 else state.current_phase


@dataclass
class AIPhaseController(BaseController):
    min_green_seconds: int = 15
    decision_interval_seconds: int = 10
    name: str = "ai"

    def choose_phase(self, state: ControllerState) -> PhaseName:
        elapsed = state.now - state.phase_started_at
        if elapsed < self.min_green_seconds or int(state.now) % self.decision_interval_seconds:
            return state.current_phase

        scores = {
            phase: sum(state.queues[lane] for lane in lanes)
            for phase, lanes in PHASE_LANES.items()
        }
        return max(scores, key=scores.get)
