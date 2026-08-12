from traffic_light.config import load_experiment_config
from traffic_light.experiments import run_experiment


def test_experiment_compares_configured_controllers():
    config = load_experiment_config("configs/experiment.yaml")
    results, summary = run_experiment(config)
    assert len(results) == len(config.controllers) * len(config.simulation.seeds)
    assert set(summary["controller"]) == {"fixed", "actuated", "ai"}
