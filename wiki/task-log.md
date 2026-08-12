# Task Log

## 2026-08-12 — Initial project scaffold

- Implemented the Model 2 project skeleton for intelligent traffic-light control.
- Added SimPy simulation, three controller strategies, experiment runner, CLI, Streamlit dashboard, FastAPI API, Docker Compose, tests, and WIKI.
- Added `AGENTS.md` with mandatory workflow rules, Ponytail guidance, Codebase Memory MCP guidance, Docker rules, and auto-commit/push policy.
- Installed Python project dependencies into `.venv`.
- Verified `pytest -q`: 4 tests passed.
- Verified `traffic-sim compare --config configs/experiment.yaml`, `traffic-sim run --config configs/base.yaml`, and `traffic-sim train --config configs/ai.yaml`.
- Verified imports for FastAPI, Streamlit, Plotly, and Gymnasium.
- Blocker: Docker CLI is not available in the current WSL environment and `sudo` requires a password, so Docker Engine could not be installed automatically here.
- Blocker: the visible `codex` executable points to WindowsApps and returns `Permission denied` from WSL, so Ponytail plugin installation could not be executed directly in this shell.
- Blocker: Codebase Memory MCP installer was attempted with `curl`, but the installation command timed out in the current network/session.
