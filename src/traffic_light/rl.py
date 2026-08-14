from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from traffic_light.config import RunConfig
from traffic_light.gym_env import TrafficLightEnv


@dataclass
class TrainingResult:
    episodes: int
    average_reward_last_10: float
    evaluation_reward: float
    evaluation_average_queue: float
    policy_path: str

    def to_dict(self) -> dict:
        return asdict(self)


def train_q_learning(
    config: RunConfig,
    episodes: int = 200,
    learning_rate: float = 0.2,
    discount: float = 0.95,
    epsilon: float = 0.2,
    policy_path: str = "outputs/q_learning_policy.json",
) -> TrainingResult:
    env = TrafficLightEnv(
        config.intersection,
        config.simulation,
        decision_interval_seconds=config.controller.decision_interval_seconds,
    )
    rng = np.random.default_rng(config.simulation.seed)
    q_table: dict[str, list[float]] = {}
    episode_rewards: list[float] = []

    for episode in range(episodes):
        observation, _ = env.reset(seed=config.simulation.seed + episode)
        state = discretize_observation(observation)
        total_reward = 0.0
        done = False
        while not done:
            action = _choose_action(q_table, state, epsilon, rng)
            next_observation, reward, terminated, truncated, _ = env.step(action)
            next_state = discretize_observation(next_observation)
            _update_q_value(q_table, state, action, reward, next_state, learning_rate, discount)
            total_reward += reward
            state = next_state
            done = terminated or truncated
        episode_rewards.append(total_reward)

    evaluation_reward, evaluation_average_queue = evaluate_q_policy(config, q_table)
    payload = {
        "type": "tabular_q_learning",
        "state": {
            "queue_bins": [0, 3, 7, 15],
            "actions": {"0": "north_south", "1": "east_west"},
        },
        "training": {
            "episodes": episodes,
            "learning_rate": learning_rate,
            "discount": discount,
            "epsilon": epsilon,
            "seed": config.simulation.seed,
        },
        "evaluation": {
            "reward": evaluation_reward,
            "average_queue": evaluation_average_queue,
        },
        "q_table": q_table,
    }
    Path(policy_path).parent.mkdir(parents=True, exist_ok=True)
    Path(policy_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return TrainingResult(
        episodes=episodes,
        average_reward_last_10=float(np.mean(episode_rewards[-10:])),
        evaluation_reward=evaluation_reward,
        evaluation_average_queue=evaluation_average_queue,
        policy_path=policy_path,
    )


def run_training_sweep(
    config: RunConfig,
    episode_values: list[int],
    output_path: str = "outputs/q_learning_sweep.json",
    csv_path: str = "outputs/q_learning_sweep.csv",
    report_path: str = "outputs/q_learning_sweep.md",
) -> pd.DataFrame:
    rows = []
    for episodes in episode_values:
        policy_path = f"outputs/q_learning_policy_{episodes}.json"
        result = train_q_learning(config, episodes=episodes, policy_path=policy_path)
        rows.append(result.to_dict())

    frame = pd.DataFrame(rows).sort_values("episodes").reset_index(drop=True)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": {
            "duration_seconds": config.simulation.duration_seconds,
            "seed": config.simulation.seed,
            "decision_interval_seconds": config.controller.decision_interval_seconds,
        },
        "runs": frame.to_dict(orient="records"),
        "best_by_average_queue": _best_sweep_row(frame),
    }
    Path(output_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    frame.to_csv(csv_path, index=False)
    Path(report_path).write_text(_build_sweep_report(frame), encoding="utf-8")
    return frame


def evaluate_q_policy(config: RunConfig, q_table: dict[str, list[float]]) -> tuple[float, float]:
    env = TrafficLightEnv(
        config.intersection,
        config.simulation,
        decision_interval_seconds=config.controller.decision_interval_seconds,
    )
    observation, _ = env.reset(seed=config.simulation.seed)
    state = discretize_observation(observation)
    total_reward = 0.0
    queues: list[float] = []
    done = False
    while not done:
        action = int(np.argmax(q_table.get(state, [0.0, 0.0])))
        observation, reward, terminated, truncated, info = env.step(action)
        state = discretize_observation(observation)
        total_reward += reward
        queues.append(float(info["total_queue"]))
        done = terminated or truncated
    return total_reward, float(np.mean(queues)) if queues else 0.0


def discretize_observation(observation: np.ndarray) -> str:
    queue_bins = [int(np.digitize(value, [0, 3, 7, 15])) for value in observation[:4]]
    phase = int(observation[4])
    return ",".join([*(str(value) for value in queue_bins), str(phase)])


def _choose_action(
    q_table: dict[str, list[float]],
    state: str,
    epsilon: float,
    rng: np.random.Generator,
) -> int:
    q_table.setdefault(state, [0.0, 0.0])
    if rng.random() < epsilon:
        return int(rng.integers(0, 2))
    return int(np.argmax(q_table[state]))


def _update_q_value(
    q_table: dict[str, list[float]],
    state: str,
    action: int,
    reward: float,
    next_state: str,
    learning_rate: float,
    discount: float,
) -> None:
    q_table.setdefault(state, [0.0, 0.0])
    q_table.setdefault(next_state, [0.0, 0.0])
    current = q_table[state][action]
    target = reward + discount * max(q_table[next_state])
    q_table[state][action] = current + learning_rate * (target - current)


def _best_sweep_row(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {}
    return frame.sort_values(["evaluation_average_queue", "episodes"]).iloc[0].to_dict()


def _build_sweep_report(frame: pd.DataFrame) -> str:
    best = _best_sweep_row(frame)
    lines = [
        "# Sweep обучения Q-learning",
        "",
        "Цель sweep — проверить, как число episode влияет на качество обученной policy.",
        "",
        "## Результаты",
        "",
        _frame_to_markdown(frame),
        "",
    ]
    if best:
        lines.extend(
            [
                "## Вывод",
                "",
                (
                    f"Минимальная средняя очередь на evaluation получена при "
                    f"{int(best['episodes'])} episode: "
                    f"{best['evaluation_average_queue']:.2f}."
                ),
                "",
            ]
        )
    return "\n".join(lines)


def _frame_to_markdown(frame: pd.DataFrame) -> str:
    columns = [
        "episodes",
        "average_reward_last_10",
        "evaluation_reward",
        "evaluation_average_queue",
        "policy_path",
    ]
    headers = [
        "Episodes",
        "Reward последних 10",
        "Evaluation reward",
        "Средняя очередь",
        "Policy",
    ]
    rows = [headers, ["---"] * len(headers)]
    for _, row in frame[columns].iterrows():
        rows.append(
            [
                f"{row['episodes']:.0f}",
                f"{row['average_reward_last_10']:.2f}",
                f"{row['evaluation_reward']:.2f}",
                f"{row['evaluation_average_queue']:.2f}",
                str(row["policy_path"]),
            ]
        )
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)
