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
