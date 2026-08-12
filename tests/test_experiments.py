from pathlib import Path

from traffic_light.config import load_experiment_config
from traffic_light.experiments import build_markdown_report, run_experiment, save_results


def test_experiment_compares_configured_controllers():
    config = load_experiment_config("configs/experiment.yaml")
    results, summary = run_experiment(config)
    assert len(results) == len(config.controllers) * len(config.simulation.seeds)
    assert set(summary["controller"]) == {"fixed", "actuated", "ai"}


def test_demo_uniform_experiment_builds_unified_report(tmp_path: Path):
    config = load_experiment_config("configs/demo_uniform.yaml")
    results, summary = run_experiment(config)
    assert set(summary["scenario"]) == {"uniform_demo"}
    assert "wait_improvement_vs_fixed_pct" in summary.columns

    report = build_markdown_report(summary, config)
    assert "Демонстрационный эксперимент" in report
    assert "Равномерная нагрузка" in report

    json_path = tmp_path / "result.json"
    csv_path = tmp_path / "summary.csv"
    report_path = tmp_path / "report.md"
    save_results(results, summary, str(json_path), str(csv_path), str(report_path), config)
    assert json_path.exists()
    assert csv_path.exists()
    assert report_path.exists()
