from __future__ import annotations

import json
from pathlib import Path

import typer

from traffic_light.config import load_experiment_config, load_run_config
from traffic_light.experiments import build_controller, run_experiment, save_results
from traffic_light.simulation import run_simulation

app = typer.Typer(help="Traffic-light discrete-event simulation CLI.")


@app.command()
def run(config: str = typer.Option(..., "--config", "-c")) -> None:
    run_config = load_run_config(config)
    controller = build_controller(
        run_config.controller,
        min_green_seconds=run_config.intersection.min_green_seconds,
    )
    result = run_simulation(run_config.intersection, run_config.simulation, controller)
    output_path = run_config.output.get("path", "outputs/run_result.json")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    typer.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


@app.command()
def compare(config: str = typer.Option(..., "--config", "-c")) -> None:
    experiment_config = load_experiment_config(config)
    results, summary = run_experiment(experiment_config)
    output_path = experiment_config.output.get("path", "outputs/compare_results.json")
    csv_path = experiment_config.output.get("summary_csv", "outputs/compare_summary.csv")
    save_results(results, summary, output_path, csv_path)
    typer.echo(summary.to_string(index=False))


@app.command()
def train(config: str = typer.Option(..., "--config", "-c")) -> None:
    run_config = load_run_config(config)
    controller = build_controller(
        run_config.controller,
        min_green_seconds=run_config.intersection.min_green_seconds,
    )
    result = run_simulation(run_config.intersection, run_config.simulation, controller)
    model_path = Path("outputs/ai_policy_baseline.json")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text(
        json.dumps(
            {
                "status": "heuristic_policy_recorded",
                "controller": controller.name,
                "seed_result": result.to_dict(),
                "note": "Stable-Baselines3 training is planned as the next AI iteration.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    typer.echo(f"Saved AI policy baseline to {model_path}")
