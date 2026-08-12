FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY pyproject.toml README.md ./
RUN mkdir -p src/traffic_light && touch src/traffic_light/__init__.py \
    && pip install --no-cache-dir -e ".[dev]"

COPY AGENTS.md ./
COPY app ./app
COPY configs ./configs
COPY src ./src
COPY tests ./tests
COPY wiki ./wiki

RUN pip install --no-cache-dir --no-deps -e .

CMD ["traffic-sim", "compare", "--config", "configs/experiment.yaml"]
