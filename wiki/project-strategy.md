# Project Strategy

## Research Goal

Develop an experimental justification for intelligent traffic-light phase control that reduces vehicle waiting time at a regulated intersection.

## Technical Strategy

- Build a transparent discrete-event simulator in Python using SimPy.
- Compare at least three control strategies:
  - fixed-time baseline;
  - actuated adaptive baseline;
  - AI-oriented pressure-based controller, later replaceable by trained RL policy.
- Use repeated seeded runs and confidence intervals for experimental claims.
- Visualize results through Streamlit and Plotly.
- Keep all commands reproducible through Docker Compose.

## Current Decision

The first implementation uses a custom SimPy model instead of SUMO to keep the scientific mechanics inspectable and easy to explain.
