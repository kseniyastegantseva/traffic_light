# Архитектура

## Среда выполнения

- Python-пакет: `traffic_light`
- CLI-точка входа: `traffic-sim`
- Dashboard: `app/dashboard.py`
- API: `app/api.py`
- Конфиги: YAML-файлы в `configs/`

## Публичный CLI

```bash
traffic-sim run --config configs/base.yaml
traffic-sim train --config configs/ai.yaml
traffic-sim compare --config configs/experiment.yaml
```

## Основные компоненты

- `config.py` валидирует YAML-конфиги через Pydantic.
- `controllers.py` содержит фиксированную, адаптивную и AI-ориентированную стратегии управления фазами.
- `simulation.py` запускает дискретно-событийную модель перекрёстка на SimPy.
- `experiments.py` выполняет сравнение стратегий по нескольким seed и сохраняет JSON/CSV-результаты.
- `gym_env.py` содержит минимальную Gymnasium-совместимую оболочку для будущего RL-обучения.

## Docker

Docker Compose содержит сервисы:

- `sim` — запуск экспериментов;
- `dashboard` — Streamlit-визуализация;
- `api` — FastAPI endpoint.

Текущий рабочий способ на машине пользователя: Docker Desktop установлен в Windows, а команды Docker доступны из PowerShell. В WSL установлен Docker CLI, но socket Docker Desktop не подключён к Ubuntu напрямую; если это понадобится, нужно включить WSL integration для дистрибутива `Ubuntu` в настройках Docker Desktop.

Для проверки без WSL bind mount используется `docker-compose.ci.yml`. Он не монтирует текущую папку внутрь контейнера и запускает код, скопированный в образ на этапе сборки.
