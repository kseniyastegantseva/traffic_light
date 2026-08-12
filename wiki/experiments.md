# Experiments

## Metrics

- Average wait time.
- Median wait time.
- Maximum wait time.
- Average queue length.
- Throughput per hour.
- Stops.
- Fairness index across directions.
- 95% confidence interval half-width for average wait time.

## Baselines

- `fixed`: switches by a constant phase duration.
- `actuated`: switches when cross-direction queue pressure is higher after minimum green.
- `ai`: pressure-maximizing controller prepared as the v1 intelligent policy baseline.

## Default Scenario

The default experiment runs five random seeds for each controller using `configs/experiment.yaml`.

## Initial Verification Result

The first seeded comparison produced the expected result ordering: adaptive and AI-oriented controllers reduced average wait time compared with the fixed-time baseline. Generated files are stored under `outputs/` locally and ignored by git.
