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
traffic-sim sweep --config configs/ai.yaml --episodes 10,25,50,100 --seeds 1,2,3,4,5
traffic-sim select-policy --config configs/ai.yaml
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

Dockerfile разделён на два target:

- `base` — лёгкий образ для CLI-симуляции и экспериментов;
- `app` — образ для dashboard/API с дополнительными UI/API-зависимостями.

## Dashboard

Dashboard по умолчанию читает `outputs/demo_uniform_results.json`, если файл существует. Он показывает:

- KPI лучшей стратегии для выбранного сценария;
- сравнение среднего ожидания с доверительным интервалом;
- улучшение относительно `fixed`;
- таблицу сводных метрик;
- распределение результатов по seed;
- среднее ожидание по направлениям;
- Markdown-отчёт эксперимента.

Dashboard теперь автоматически ищет файлы `outputs/*_results.json`. Приоритетный файл для полного просмотра — `outputs/experiment_suite_results.json`, если он уже сгенерирован.

Вкладка `Аналитика` использует блок `analytics` из JSON-результата эксперимента и показывает:

- средний ранг стратегии;
- среднее улучшение относительно `fixed`;
- таблицу агрегированных показателей по стратегиям;
- сравнение `ai` и `actuated`;
- рейтинг стратегий по каждому сценарию.

## RL-контур

`gym_env.py` задаёт Gymnasium-совместимую среду для выбора фазы светофора:

- observation: очереди `north`, `south`, `east`, `west` и текущая фаза;
- action `0`: фаза `north_south`;
- action `1`: фаза `east_west`;
- reward: отрицательная сумма очередей с небольшим штрафом за переключение фазы;
- episode: последовательность decision-интервалов внутри заданной длительности симуляции.

`rl.py` реализует первый обучаемый baseline: табличный Q-learning. Он нужен как прозрачная промежуточная ступень перед подключением Stable-Baselines3.

Команда:

```bash
traffic-sim train --config configs/ai.yaml --episodes 200
```

Результат сохраняется в `outputs/q_learning_policy.json`.

Команда:

```bash
traffic-sim sweep --config configs/ai.yaml --episodes 10,25,50,100 --seeds 1,2,3,4,5
```

запускает серию обучений Q-learning с разным числом эпизодов и seed, сохраняет отдельные policy-файлы `outputs/q_learning_policy_<episodes>_seed_<seed>.json` и формирует `outputs/q_learning_sweep.json`, `outputs/q_learning_sweep.csv`, `outputs/q_learning_sweep_summary.csv`, `outputs/q_learning_sweep.md`. Этот контур нужен для выбора разумной длительности обучения перед большим сравнением стратегий.

Команда:

```bash
traffic-sim select-policy --config configs/ai.yaml
```

читает `outputs/q_learning_sweep.json`, выбирает лучший конкретный policy-файл из лучшего sweep-варианта и копирует его в стандартный путь `outputs/q_learning_policy.json`, который использует контроллер `q_learning`.

После обучения policy может использоваться в SimPy-экспериментах через контроллер `q_learning`. Он читает Q-table из JSON, выбирает фазу с максимальным Q-значением, а для неизвестного состояния использует pressure-based fallback.
