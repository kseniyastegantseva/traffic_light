# Журнал задач

## 2026-08-12 — Первичный каркас проекта

- Реализован каркас Модели 2 для интеллектуального управления светофором.
- Добавлены SimPy-симуляция, три стратегии управления, runner экспериментов, CLI, Streamlit dashboard, FastAPI API, Docker Compose, тесты и WIKI.
- Добавлен `AGENTS.md` с правилами работы, Docker-подходом, автообновлением WIKI и политикой commit/push.
- Python-зависимости установлены в `.venv`.
- Проверено `pytest -q`: 4 теста прошли.
- Проверены команды `traffic-sim compare --config configs/experiment.yaml`, `traffic-sim run --config configs/base.yaml` и `traffic-sim train --config configs/ai.yaml`.
- Проверены импорты FastAPI, Streamlit, Plotly и Gymnasium.
- Первый push в `origin/main` выполнен успешно.

## 2026-08-12 — Настройка Docker Desktop

- Пользователь установил Docker Desktop в Windows.
- Проверено, что Docker Desktop daemon работает через Windows Docker CLI.
- Исправлена проблема текущего PowerShell PATH: добавлен путь `AppData/Local/Programs/DockerDesktop/resources/bin`, чтобы находился `docker-credential-desktop`.
- Команда `docker run --rm hello-world` успешно выполнена через Docker Desktop.
- В WSL Docker CLI и Compose доступны, но Ubuntu пока не подключена к socket Docker Desktop напрямую; при необходимости нужно включить WSL integration для дистрибутива `Ubuntu`.
- Добавлен `docker-compose.ci.yml` без bind mount как рабочий Docker-путь, когда Docker Desktop доступен из Windows, но WSL integration ещё не настроена.
- По просьбе пользователя этапы Ponytail и Codebase Memory MCP временно пропущены и больше не считаются блокером текущего этапа.
- WIKI и проектная документация переведены на русский язык; в `AGENTS.md` закреплено правило вести документацию на русском.

## 2026-08-12 — Демонстрационный равномерный сценарий и dashboard

- Добавлен `configs/demo_uniform.yaml` с равномерной нагрузкой 6 автомобилей в минуту по каждому направлению.
- Расширен экспериментальный runner: теперь он поддерживает именованные сценарии, добавляет поля `scenario` и `scenario_title`, считает улучшение среднего ожидания относительно `fixed`.
- Добавлена генерация единого Markdown-отчёта эксперимента.
- Улучшен Streamlit dashboard: добавлены KPI, выбор файла результатов, выбор сценария, графики ожидания, улучшения к `fixed`, распределения по seed, ожидания по направлениям и вкладка Markdown-отчёта.
- Локально сгенерированы `outputs/demo_uniform_results.json`, `outputs/demo_uniform_summary.csv`, `outputs/demo_uniform_report.md`.
- Локальный dashboard запущен на `http://localhost:8501` и проверен HTTP-ответом `200 OK`.
- Dockerfile разделён на target `base` для экспериментов и target `app` для dashboard/API, чтобы ускорить сборку CLI-образа.
- Проверено `docker compose -f docker-compose.ci.yml run --rm --no-deps sim traffic-sim compare --config configs/demo_uniform.yaml`: демонстрационный эксперимент успешно выполняется в свежем Docker-образе.

## 2026-08-14 — Набор исследовательских сценариев

- Добавлен `configs/experiment_suite.yaml` с пятью сценариями: равномерная нагрузка, низкая нагрузка, утренний пик north/south, вечерний пик east/west, перегруженный перекрёсток.
- Dashboard теперь автоматически видит новые файлы `outputs/*_results.json` и отдаёт приоритет `outputs/experiment_suite_results.json`.
- Сгенерирован единый отчёт `outputs/experiment_suite_report.md`, сводка `outputs/experiment_suite_summary.csv` и подробные результаты `outputs/experiment_suite_results.json`.
- Проверено `traffic-sim compare --config configs/experiment_suite.yaml`.
- Проверено `ruff check .`: без ошибок.
- Проверено `pytest -q`: 6 тестов прошли.

## Текущие проблемы и решения

- Git push из WSL может зависать на GitHub credential. Решение: выполнять `git push origin main` вручную в авторизованной среде либо настроить credential helper для WSL.
- Docker Desktop без WSL integration не монтирует WSL-папку как volume. Решение: для CLI-проверок использовать `docker-compose.ci.yml` без bind mount; для live-разработки включить WSL integration для Ubuntu в Docker Desktop.
- Dashboard требует предварительно сгенерированных файлов `outputs/*_results.json`. Решение: перед просмотром запускать `traffic-sim compare --config configs/experiment_suite.yaml`.

## 2026-08-14 — Аналитика для научного отчёта

- Добавлен аналитический слой в JSON-результат эксперимента: `scenario_ranking`, `strategy_overview`, `ai_vs_actuated`.
- Markdown-отчёт теперь содержит рейтинг стратегий по сценариям, агрегированную сводку по стратегиям и сравнение `ai` против `actuated`.
- Dashboard расширен вкладкой `Аналитика` с графиками среднего ранга, среднего улучшения относительно `fixed`, сравнением AI-vs-adaptive и таблицами.
- Проверено `traffic-sim compare --config configs/experiment_suite.yaml`.
- Проверено `ruff check .`: без ошибок.
- Проверено `pytest -q`: 7 тестов прошли.
- Проверено Docker: `docker compose -f docker-compose.ci.yml build sim` и `docker compose -f docker-compose.ci.yml run --rm --no-deps sim traffic-sim compare --config configs/experiment_suite.yaml`.

## 2026-08-14 — Первый RL baseline

- `gym_env.py` заменён с простой заготовки на Gymnasium-совместимую среду перекрёстка с очередями, фазой, действиями и reward.
- Добавлен `rl.py` с табличным Q-learning обучением, greedy evaluation и сохранением policy в JSON.
- Команда `traffic-sim train --config configs/ai.yaml --episodes N` теперь обучает Q-learning policy вместо записи эвристического placeholder.
- В `configs/ai.yaml` добавлен `output.policy_path`.
- Проверено `traffic-sim train --config configs/ai.yaml --episodes 20`: создан `outputs/q_learning_policy.json`.
- Проверено `ruff check .`: без ошибок.
- Проверено `pytest -q`: 10 тестов прошли.

## 2026-08-14 — Подключение Q-learning policy к SimPy-сравнению

- Добавлен контроллер `QLearningPolicyController`, который читает `outputs/q_learning_policy.json` и выбирает фазу по Q-table.
- Добавлен тип контроллера `q_learning` в конфигурации.
- Добавлен `configs/experiment_suite_rl.yaml` для сравнения `fixed`, `actuated`, `ai` и `q_learning` на пяти исследовательских сценариях.
- Dashboard теперь приоритетно открывает `outputs/experiment_suite_rl_results.json`, если файл уже сгенерирован.
- Проверено `traffic-sim train --config configs/ai.yaml --episodes 50`.
- Проверено `traffic-sim compare --config configs/experiment_suite_rl.yaml`.
- Проверено Docker в одном контейнере: `docker compose -f docker-compose.ci.yml run --rm --no-deps sim sh -lc "traffic-sim train --config configs/ai.yaml --episodes 5 && traffic-sim compare --config configs/experiment_suite_rl.yaml"`.
- Проверено `ruff check .`: без ошибок.
- Проверено `pytest -q`: 12 тестов прошли.

## 2026-08-14 — Sweep обучения Q-learning

- Добавлена команда `traffic-sim sweep --config configs/ai.yaml --episodes 10,25,50,100` для серии обучений Q-learning с разным числом эпизодов.
- Добавлена функция `run_training_sweep`, которая сохраняет JSON, CSV, Markdown-отчёт и отдельные policy-файлы.
- Добавлен unit-тест на сохранение sweep-отчёта.
- Проверено `traffic-sim sweep --config configs/ai.yaml --episodes 5,10,20`: сформированы `outputs/q_learning_sweep.json`, `outputs/q_learning_sweep.csv`, `outputs/q_learning_sweep.md`.
- Проверено Docker: `docker compose -f docker-compose.ci.yml build sim` и `docker compose -f docker-compose.ci.yml run --rm --no-deps sim traffic-sim sweep --config configs/ai.yaml --episodes 2,3`.
- Проверено `ruff check .`: без ошибок.
- Проверено `pytest -q`: 13 тестов прошли.

## 2026-08-14 — Multi-seed sweep Q-learning

- Команда `traffic-sim sweep` расширена параметром `--seeds`, например `--seeds 1,2,3,4,5`.
- Sweep теперь сохраняет подробные строки по каждому seed в `outputs/q_learning_sweep.csv` и агрегированную сводку по episodes в `outputs/q_learning_sweep_summary.csv`.
- JSON-результат содержит `runs`, `summary` и лучший вариант по средней очереди.
- Markdown-отчёт показывает агрегированную сводку, подробные прогоны и 95% доверительный интервал средней очереди.
- Проверено `traffic-sim sweep --config configs/ai.yaml --episodes 2,3 --seeds 11,12`.
- Проверено Docker: `docker compose -f docker-compose.ci.yml build sim` и `docker compose -f docker-compose.ci.yml run --rm --no-deps sim traffic-sim sweep --config configs/ai.yaml --episodes 2,3 --seeds 11,12`.
- Проверено `ruff check .`: без ошибок.
- Проверено `pytest -q`: 13 тестов прошли.
