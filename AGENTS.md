# AGENTS.md

## Project Mission

This repository implements only **Model 2: intelligent traffic light control** for a regulated intersection.
Model 1, photo analysis, is out of scope until explicitly requested.

Research topic: improving traffic-flow management at a signalized intersection using AI algorithms, with experimental justification through discrete-event simulation.

Primary goal: prove whether intelligent phase control reduces vehicle waiting time compared with baseline signal strategies.

## Mandatory Agent Workflow

Before every new task:

1. Read this file.
2. Read the current WIKI entry point: `wiki/README.md`.
3. Check the task journal: `wiki/task-log.md`.
4. Use existing project patterns before adding new abstractions.

After every completed task:

1. Update the relevant WIKI pages.
2. Add a short entry to `wiki/task-log.md`.
3. Run the relevant tests or document why they could not be run.
4. Commit and push changes to `origin/main`, unless the user asks for another branch.

## Engineering Rules

- Develop and run the project through Docker whenever Docker is available.
- Keep code minimal and understandable: prefer the standard library, existing dependencies, and simple interfaces.
- Do not implement Model 1 code in this repository phase.
- Keep experiments reproducible through explicit configs and random seeds.
- Store generated experiment outputs under `outputs/`; do not commit large generated files unless explicitly needed.
- Public interfaces must remain stable once documented in `wiki/architecture.md`.

## Ponytail

Use Ponytail principles throughout this project:

- Does this need to exist? If not, skip it.
- Is it already in the codebase? Reuse it.
- Does Python or an installed dependency already solve it? Use that.
- Add only the minimum code needed for the task, without removing validation, reproducibility, or tests.

Installation command for Codex environments:

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

If `codex` or Node.js is unavailable in the execution environment, record that blocker in `wiki/task-log.md` and continue with the written rules above.

## Codebase Memory MCP

Use Codebase Memory MCP for codebase indexing and project memory whenever available.

Installation command for Linux/WSL:

```bash
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash
```

After installation, restart the agent/session if required and index this repository. If the MCP tools are not available in the active session, continue using `rg`, tests, and the WIKI as the project memory source.

## Core Stack

- Python 3.12
- SimPy for discrete-event traffic simulation
- Gymnasium-compatible environment for AI-controller experiments
- Typer CLI
- FastAPI API surface
- Streamlit + Plotly dashboard
- Docker Compose for local execution
