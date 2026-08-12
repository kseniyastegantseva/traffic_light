# Architecture

## Runtime

- Python package: `traffic_light`
- CLI entrypoint: `traffic-sim`
- Dashboard: `app/dashboard.py`
- API: `app/api.py`
- Configs: YAML files under `configs/`

## Public CLI

```bash
traffic-sim run --config configs/base.yaml
traffic-sim train --config configs/ai.yaml
traffic-sim compare --config configs/experiment.yaml
```

## Core Components

- `config.py` validates YAML configs with Pydantic.
- `controllers.py` contains fixed-time, actuated, and AI-oriented phase controllers.
- `simulation.py` runs the SimPy discrete-event intersection model.
- `experiments.py` runs seeded comparisons and saves JSON/CSV outputs.
- `gym_env.py` provides a small Gymnasium-compatible shell for future RL training.

## Docker

Use Docker Compose services:

- `sim` for experiments;
- `dashboard` for Streamlit visualization;
- `api` for FastAPI endpoints.

Current environment note: Docker files are present and ready, but Docker CLI was not available in the WSL shell used for the initial scaffold.
