import json
from pathlib import Path

from traffic_light.config import load_run_config
from traffic_light.controllers import ControllerState, QLearningPolicyController
from traffic_light.experiments import run_experiment
from traffic_light.gym_env import TrafficLightEnv
from traffic_light.rl import discretize_observation, train_q_learning


def test_traffic_light_env_is_reproducible_for_seed():
    config = load_run_config("configs/ai.yaml")
    first = TrafficLightEnv(
        config.intersection,
        config.simulation,
        decision_interval_seconds=config.controller.decision_interval_seconds,
    )
    second = TrafficLightEnv(
        config.intersection,
        config.simulation,
        decision_interval_seconds=config.controller.decision_interval_seconds,
    )
    first_observation, _ = first.reset(seed=123)
    second_observation, _ = second.reset(seed=123)
    assert first_observation.tolist() == second_observation.tolist()

    first_next, first_reward, *_ = first.step(0)
    second_next, second_reward, *_ = second.step(0)
    assert first_next.tolist() == second_next.tolist()
    assert first_reward == second_reward


def test_discretize_observation_includes_phase():
    assert discretize_observation([0, 4, 8, 20, 1]) == "1,2,3,4,1"


def test_q_learning_training_saves_policy(tmp_path: Path):
    config = load_run_config("configs/ai.yaml")
    policy_path = tmp_path / "policy.json"
    result = train_q_learning(config, episodes=3, policy_path=str(policy_path))

    assert policy_path.exists()
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    assert payload["type"] == "tabular_q_learning"
    assert payload["training"]["episodes"] == 3
    assert payload["q_table"]
    assert result.policy_path == str(policy_path)


def test_q_learning_controller_uses_saved_policy(tmp_path: Path):
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "type": "tabular_q_learning",
                "q_table": {
                    "1,1,4,4,0": [0.0, 10.0],
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    controller = QLearningPolicyController(
        policy_path=str(policy_path),
        min_green_seconds=1,
        decision_interval_seconds=1,
    )
    phase = controller.choose_phase(
        ControllerState(
            now=10,
            current_phase="north_south",
            phase_started_at=0,
            queues={"north": 1, "south": 1, "east": 20, "west": 20},
        )
    )
    assert phase == "east_west"


def test_experiment_suite_with_q_learning_policy_runs(tmp_path: Path, monkeypatch):
    config = load_run_config("configs/ai.yaml")
    policy_path = Path("outputs/q_learning_policy.json")
    if not policy_path.exists():
        train_q_learning(config, episodes=3, policy_path=str(policy_path))

    from traffic_light.config import load_experiment_config

    experiment_config = load_experiment_config("configs/experiment_suite_rl.yaml")
    experiment_config.simulation.seeds = [1]
    experiment_config.scenarios = experiment_config.scenarios[:1] if experiment_config.scenarios else None
    results, summary = run_experiment(experiment_config)
    assert len(results) == 4
    assert "q_learning" in set(summary["controller"])
