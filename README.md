# Интеллектуальное управление светофором

Проект посвящён дискретно-событийному моделированию регулируемого перекрёстка и экспериментальному сравнению стратегий управления фазами светофора.

Текущий этап охватывает только **Модель 2 — интеллектуальный светофор**. **Модель 1 — анализ фотографии** пока не реализуется.

## Быстрый старт через Docker

```bash
docker compose build
docker compose run --rm sim traffic-sim compare --config configs/demo_uniform.yaml
docker compose up dashboard
```

Dashboard будет доступен на `http://localhost:8501`.

Если Docker Desktop запускается из Windows, а WSL integration для Ubuntu ещё не включена, используйте compose-файл без bind mount:

```bash
docker compose -f docker-compose.ci.yml build
docker compose -f docker-compose.ci.yml run --rm sim traffic-sim compare --config configs/demo_uniform.yaml
docker compose -f docker-compose.ci.yml up dashboard
```

`sim`-образ собирается на лёгком Docker target `base`. Dashboard и API используют target `app`, куда дополнительно устанавливаются Streamlit, Plotly и FastAPI.

## Запуск без Docker

```bash
python -m pip install -e ".[dev]"
traffic-sim compare --config configs/demo_uniform.yaml
streamlit run app/dashboard.py
```

## Основные команды

```bash
traffic-sim run --config configs/base.yaml
traffic-sim train --config configs/ai.yaml
traffic-sim sweep --config configs/ai.yaml --episodes 10,25,50,100 --seeds 1,2,3,4,5
traffic-sim compare --config configs/experiment.yaml
traffic-sim compare --config configs/demo_uniform.yaml
traffic-sim compare --config configs/experiment_suite.yaml
traffic-sim compare --config configs/experiment_suite_rl.yaml
```

## Обучение первого RL baseline

```bash
traffic-sim train --config configs/ai.yaml --episodes 200
```

Команда обучает табличную Q-learning policy в Gymnasium-совместимой среде и сохраняет её в `outputs/q_learning_policy.json`.

Чтобы проверить, как число эпизодов влияет на качество policy, используйте sweep:

```bash
traffic-sim sweep --config configs/ai.yaml --episodes 10,25,50,100 --seeds 1,2,3,4,5
```

Sweep сохраняет:

- `outputs/q_learning_sweep.json` — машинно-читаемые результаты;
- `outputs/q_learning_sweep.csv` — подробные прогоны по каждому seed;
- `outputs/q_learning_sweep_summary.csv` — агрегированную сводку по episodes;
- `outputs/q_learning_sweep.md` — краткий Markdown-отчёт;
- `outputs/q_learning_policy_<episodes>_seed_<seed>.json` — отдельную policy для каждой пары episodes/seed.

После обучения policy можно включить в общий эксперимент:

```bash
traffic-sim compare --config configs/experiment_suite_rl.yaml
```

В `docker-compose.ci.yml` нет bind mount, поэтому для проверки Q-learning в Docker запускайте обучение и сравнение в одном контейнере:

```bash
docker compose -f docker-compose.ci.yml run --rm --no-deps sim sh -lc "traffic-sim train --config configs/ai.yaml --episodes 50 && traffic-sim compare --config configs/experiment_suite_rl.yaml"
```

Для полного первичного сравнения стратегий используйте:

```bash
traffic-sim compare --config configs/experiment_suite.yaml
```

Проектная память, решения и журнал задач ведутся в `wiki/`.
