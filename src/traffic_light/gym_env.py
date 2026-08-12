from __future__ import annotations

from typing import ClassVar

import numpy as np

try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError:  # pragma: no cover
    gym = None
    spaces = None


class TrafficLightEnv(gym.Env if gym else object):
    """Small Gymnasium-compatible shell for future RL experiments."""

    metadata: ClassVar[dict[str, list[str]]] = {"render_modes": []}

    def __init__(self, max_queue: int = 50):
        if gym is None:
            raise ImportError("Install gymnasium to use TrafficLightEnv.")
        self.max_queue = max_queue
        self.observation_space = spaces.Box(low=0, high=max_queue, shape=(4,), dtype=np.float32)
        self.action_space = spaces.Discrete(2)
        self.state = np.zeros(4, dtype=np.float32)

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self.state = np.zeros(4, dtype=np.float32)
        return self.state, {}

    def step(self, action: int):
        served = np.array([1, 1, 0, 0]) if action == 0 else np.array([0, 0, 1, 1])
        arrivals = self.np_random.poisson([1.0, 1.0, 0.7, 0.7])
        self.state = np.clip(self.state + arrivals - served, 0, self.max_queue)
        reward = -float(self.state.sum())
        return self.state, reward, False, False, {}
