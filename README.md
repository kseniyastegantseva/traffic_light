# Интеллектуальное управление светофором

Проект посвящён дискретно-событийному моделированию регулируемого перекрёстка и экспериментальному сравнению стратегий управления фазами светофора.

Текущий этап охватывает только **Модель 2 — интеллектуальный светофор**. **Модель 1 — анализ фотографии** пока не реализуется.

## Быстрый старт через Docker

```bash
docker compose build
docker compose run --rm sim traffic-sim compare --config configs/experiment.yaml
docker compose up dashboard
```

Dashboard будет доступен на `http://localhost:8501`.

Если Docker Desktop запускается из Windows, а WSL integration для Ubuntu ещё не включена, используйте compose-файл без bind mount:

```bash
docker compose -f docker-compose.ci.yml build
docker compose -f docker-compose.ci.yml run --rm sim traffic-sim compare --config configs/experiment.yaml
docker compose -f docker-compose.ci.yml up dashboard
```

## Запуск без Docker

```bash
python -m pip install -e ".[dev]"
traffic-sim compare --config configs/experiment.yaml
streamlit run app/dashboard.py
```

## Основные команды

```bash
traffic-sim run --config configs/base.yaml
traffic-sim train --config configs/ai.yaml
traffic-sim compare --config configs/experiment.yaml
```

Проектная память, решения и журнал задач ведутся в `wiki/`.
