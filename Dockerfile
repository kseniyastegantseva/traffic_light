FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY pyproject.toml README.md ./
COPY src ./src
COPY app ./app
COPY configs ./configs
COPY tests ./tests
COPY wiki ./wiki
COPY AGENTS.md ./

RUN pip install --no-cache-dir -e ".[dev]"

CMD ["traffic-sim", "compare", "--config", "configs/experiment.yaml"]
