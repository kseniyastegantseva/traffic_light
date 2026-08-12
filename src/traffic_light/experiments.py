from __future__ import annotations

import json
from pathlib import Path
from statistics import stdev

import pandas as pd

from traffic_light.config import ControllerConfig, ExperimentConfig, SimulationConfig
from traffic_light.controllers import (
    ActuatedController,
    AIPhaseController,
    BaseController,
    FixedTimeController,
)
from traffic_light.simulation import SimulationResult, run_simulation


def build_controller(config: ControllerConfig, min_green_seconds: int) -> BaseController:
    if config.type == "fixed":
        return FixedTimeController(phase_duration_seconds=config.phase_duration_seconds)
    if config.type == "actuated":
        return ActuatedController(
            min_green_seconds=min_green_seconds,
            decision_interval_seconds=config.decision_interval_seconds,
        )
    return AIPhaseController(
        min_green_seconds=min_green_seconds,
        decision_interval_seconds=config.decision_interval_seconds,
    )


def run_experiment(config: ExperimentConfig) -> tuple[list[SimulationResult], pd.DataFrame]:
    results: list[SimulationResult] = []
    for controller_config in config.controllers:
        for seed in config.simulation.seeds:
            simulation = SimulationConfig(
                duration_seconds=config.simulation.duration_seconds,
                seed=seed,
                service_time_seconds=config.simulation.service_time_seconds,
            )
            controller = build_controller(
                controller_config,
                min_green_seconds=config.intersection.min_green_seconds,
            )
            results.append(run_simulation(config.intersection, simulation, controller))

    rows = [result.to_dict() for result in results]
    frame = pd.DataFrame(rows)
    summary = (
        frame.groupby("controller")
        .agg(
            runs=("seed", "count"),
            average_wait_seconds=("average_wait_seconds", "mean"),
            wait_std=("average_wait_seconds", _std_or_zero),
            median_wait_seconds=("median_wait_seconds", "mean"),
            average_queue_length=("average_queue_length", "mean"),
            throughput_per_hour=("throughput_per_hour", "mean"),
            fairness_index=("fairness_index", "mean"),
            stops=("stops", "mean"),
        )
        .reset_index()
    )
    summary["wait_95ci_half_width"] = summary.apply(
        lambda row: 1.96 * row["wait_std"] / (row["runs"] ** 0.5),
        axis=1,
    )
    return results, summary


def save_results(results: list[SimulationResult], summary: pd.DataFrame, path: str, csv_path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "runs": [result.to_dict() for result in results],
        "summary": summary.to_dict(orient="records"),
    }
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary.to_csv(csv_path, index=False)


def _std_or_zero(values) -> float:
    values = list(values)
    return stdev(values) if len(values) > 1 else 0.0
