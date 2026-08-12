# Intelligent Traffic Light Control

Discrete-event simulation and experimental comparison of traffic-light phase control strategies for a regulated intersection.

This repository currently covers only **Model 2: intelligent traffic light control**.

## Quick Start

```bash
docker compose build
docker compose run --rm sim traffic-sim compare --config configs/experiment.yaml
docker compose up dashboard
```

Without Docker:

```bash
python -m pip install -e ".[dev]"
traffic-sim compare --config configs/experiment.yaml
streamlit run app/dashboard.py
```

## Main Interfaces

```bash
traffic-sim run --config configs/base.yaml
traffic-sim train --config configs/ai.yaml
traffic-sim compare --config configs/experiment.yaml
```

Project memory and decisions live in `wiki/`.
