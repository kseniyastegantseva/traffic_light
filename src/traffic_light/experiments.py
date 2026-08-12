from __future__ import annotations

import json
from pathlib import Path
from statistics import stdev

import pandas as pd

from traffic_light.config import (
    ControllerConfig,
    ExperimentConfig,
    IntersectionConfig,
    SimulationConfig,
)
from traffic_light.controllers import (
    ActuatedController,
    AIPhaseController,
    BaseController,
    FixedTimeController,
)
from traffic_light.simulation import run_simulation

BASELINE_CONTROLLER = "fixed"


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


def run_experiment(config: ExperimentConfig) -> tuple[list[dict], pd.DataFrame]:
    rows: list[dict] = []
    for scenario in _iter_scenarios(config):
        for controller_config in config.controllers:
            for seed in config.simulation.seeds:
                simulation = SimulationConfig(
                    duration_seconds=config.simulation.duration_seconds,
                    seed=seed,
                    service_time_seconds=config.simulation.service_time_seconds,
                )
                controller = build_controller(
                    controller_config,
                    min_green_seconds=scenario["intersection"].min_green_seconds,
                )
                result = run_simulation(scenario["intersection"], simulation, controller)
                rows.append(
                    {
                        "scenario": scenario["name"],
                        "scenario_title": scenario["title"],
                        "scenario_description": scenario["description"],
                        **result.to_dict(),
                    }
                )

    frame = pd.DataFrame(rows)
    summary = (
        frame.groupby(["scenario", "scenario_title", "controller"])
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
    summary = _add_baseline_improvement(summary)
    return rows, summary


def save_results(
    results: list[dict],
    summary: pd.DataFrame,
    path: str,
    csv_path: str,
    report_path: str,
    config: ExperimentConfig | None = None,
) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "experiment": {
            "name": config.name if config else "experiment",
            "title": config.title if config else "Эксперимент",
            "description": config.description if config else "",
        },
        "runs": results,
        "summary": summary.to_dict(orient="records"),
    }
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary.to_csv(csv_path, index=False)
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text(
        build_markdown_report(summary, config),
        encoding="utf-8",
    )


def build_markdown_report(summary: pd.DataFrame, config: ExperimentConfig | None = None) -> str:
    title = config.title if config else "Экспериментальный отчёт"
    description = config.description if config else ""
    lines = [
        f"# {title}",
        "",
    ]
    if description:
        lines.extend([description, ""])
    lines.extend(
        [
            "## Методика",
            "",
            (
                "Для каждого сценария все стратегии запускаются на одинаковом наборе random seed. "
                "Ключевым baseline считается стратегия `fixed`; улучшение считается как снижение "
                "среднего времени ожидания относительно неё."
            ),
            "",
            "## Сводная таблица",
            "",
            _to_markdown_table(summary),
            "",
            "## Основные выводы",
            "",
        ]
    )
    for scenario, scenario_frame in summary.groupby("scenario_title", sort=False):
        best = scenario_frame.sort_values("average_wait_seconds").iloc[0]
        lines.append(
            f"- `{scenario}`: лучшая стратегия `{best['controller']}` со средним ожиданием "
            f"{best['average_wait_seconds']:.2f} с."
        )
    return "\n".join(lines) + "\n"


def _std_or_zero(values) -> float:
    values = list(values)
    return stdev(values) if len(values) > 1 else 0.0


def _iter_scenarios(config: ExperimentConfig) -> list[dict[str, str | IntersectionConfig]]:
    if config.scenarios:
        return [
            {
                "name": scenario.name,
                "title": scenario.title,
                "description": scenario.description,
                "intersection": scenario.intersection,
            }
            for scenario in config.scenarios
        ]
    if config.intersection:
        return [
            {
                "name": "default",
                "title": "Базовый сценарий",
                "description": "Сценарий из корневого поля intersection.",
                "intersection": config.intersection,
            }
        ]
    raise ValueError("Experiment config must define either intersection or scenarios.")


def _add_baseline_improvement(summary: pd.DataFrame) -> pd.DataFrame:
    summary = summary.copy()
    summary["wait_improvement_vs_fixed_pct"] = 0.0
    for scenario in summary["scenario"].unique():
        mask = summary["scenario"] == scenario
        baseline = summary.loc[mask & (summary["controller"] == BASELINE_CONTROLLER)]
        if baseline.empty:
            continue
        baseline_wait = float(baseline.iloc[0]["average_wait_seconds"])
        if baseline_wait <= 0:
            continue
        summary.loc[mask, "wait_improvement_vs_fixed_pct"] = (
            (baseline_wait - summary.loc[mask, "average_wait_seconds"]) / baseline_wait * 100
        )
    return summary


def _to_markdown_table(frame: pd.DataFrame) -> str:
    columns = [
        "scenario_title",
        "controller",
        "runs",
        "average_wait_seconds",
        "median_wait_seconds",
        "average_queue_length",
        "throughput_per_hour",
        "fairness_index",
        "wait_improvement_vs_fixed_pct",
    ]
    display = frame[columns].copy()
    rename = {
        "scenario_title": "Сценарий",
        "controller": "Стратегия",
        "runs": "Запуски",
        "average_wait_seconds": "Среднее ожидание, с",
        "median_wait_seconds": "Медианное ожидание, с",
        "average_queue_length": "Средняя очередь",
        "throughput_per_hour": "Пропускная способность/час",
        "fairness_index": "Справедливость",
        "wait_improvement_vs_fixed_pct": "Улучшение к fixed, %",
    }
    display = display.rename(columns=rename)
    for column in display.select_dtypes(include="number").columns:
        if column == "Запуски":
            display[column] = display[column].map(lambda value: f"{value:.0f}")
        else:
            display[column] = display[column].map(lambda value: f"{value:.2f}")
    headers = list(display.columns)
    rows = [[str(value) for value in row] for row in display.to_numpy().tolist()]
    separator = ["---"] * len(headers)
    table_rows = [headers, separator, *rows]
    return "\n".join("| " + " | ".join(row) + " |" for row in table_rows)
