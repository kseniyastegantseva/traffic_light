from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DEFAULT_RESULT_FILES = [
    Path("outputs/experiment_suite_results.json"),
    Path("outputs/demo_uniform_results.json"),
    Path("outputs/compare_results.json"),
]

CONTROLLER_LABELS = {
    "fixed": "Фиксированная",
    "actuated": "Адаптивная",
    "ai": "AI baseline",
}

COLOR_MAP = {
    "fixed": "#6B7280",
    "actuated": "#2563EB",
    "ai": "#059669",
}


def main() -> None:
    st.set_page_config(page_title="Интеллектуальный светофор", layout="wide")

    result_path = _select_result_file()
    if result_path is None:
        st.title("Интеллектуальный светофор")
        st.info("Сначала запустите `traffic-sim compare --config configs/demo_uniform.yaml`.")
        st.stop()

    payload = json.loads(result_path.read_text(encoding="utf-8"))
    runs = pd.DataFrame(payload["runs"])
    summary = pd.DataFrame(payload["summary"])
    analytics = payload.get("analytics", {})
    strategy_overview = pd.DataFrame(analytics.get("strategy_overview", []))
    scenario_ranking = pd.DataFrame(analytics.get("scenario_ranking", []))
    ai_vs_actuated = pd.DataFrame(analytics.get("ai_vs_actuated", []))
    experiment = payload.get("experiment", {})

    st.title(experiment.get("title") or "Интеллектуальный светофор")
    if experiment.get("description"):
        st.caption(experiment["description"])

    scenarios = list(summary["scenario_title"].drop_duplicates())
    selected_scenario = st.sidebar.selectbox("Сценарий", scenarios)
    scenario_summary = summary[summary["scenario_title"] == selected_scenario].copy()
    scenario_runs = runs[runs["scenario_title"] == selected_scenario].copy()

    best = scenario_summary.sort_values("average_wait_seconds").iloc[0]
    fixed = scenario_summary[scenario_summary["controller"] == "fixed"].iloc[0]
    improvement = best["wait_improvement_vs_fixed_pct"]

    kpi_a, kpi_b, kpi_c, kpi_d = st.columns(4)
    kpi_a.metric("Лучшая стратегия", _label(best["controller"]))
    kpi_b.metric("Среднее ожидание", f"{best['average_wait_seconds']:.2f} с")
    kpi_c.metric("Улучшение к fixed", f"{improvement:.1f}%")
    kpi_d.metric("Fixed baseline", f"{fixed['average_wait_seconds']:.2f} с")

    summary_tab, analytics_tab, runs_tab, report_tab = st.tabs(
        ["Сводка", "Аналитика", "Запуски", "Отчёт"]
    )

    with summary_tab:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(
                px.bar(
                    scenario_summary,
                    x="controller",
                    y="average_wait_seconds",
                    error_y="wait_95ci_half_width",
                    color="controller",
                    color_discrete_map=COLOR_MAP,
                    labels={
                        "controller": "Стратегия",
                        "average_wait_seconds": "Среднее ожидание, с",
                        "wait_95ci_half_width": "95% ДИ",
                    },
                    title="Среднее время ожидания",
                ).update_xaxes(labelalias=CONTROLLER_LABELS),
                use_container_width=True,
            )
        with right:
            st.plotly_chart(
                px.bar(
                    scenario_summary,
                    x="controller",
                    y="wait_improvement_vs_fixed_pct",
                    color="controller",
                    color_discrete_map=COLOR_MAP,
                    labels={
                        "controller": "Стратегия",
                        "wait_improvement_vs_fixed_pct": "Улучшение к fixed, %",
                    },
                    title="Снижение ожидания относительно fixed",
                ).update_xaxes(labelalias=CONTROLLER_LABELS),
                use_container_width=True,
            )

        st.dataframe(
            _format_summary(scenario_summary),
            use_container_width=True,
            hide_index=True,
        )

    with analytics_tab:
        if strategy_overview.empty or scenario_ranking.empty:
            st.info("Для выбранного файла нет расширенной аналитики. Перезапустите эксперимент.")
        else:
            left, right = st.columns(2)
            with left:
                st.plotly_chart(
                    px.bar(
                        strategy_overview.sort_values("mean_rank"),
                        x="controller",
                        y="mean_rank",
                        color="controller",
                        color_discrete_map=COLOR_MAP,
                        labels={
                            "controller": "Стратегия",
                            "mean_rank": "Средний ранг",
                        },
                        title="Средний ранг стратегии по всем сценариям",
                    ).update_xaxes(labelalias=CONTROLLER_LABELS),
                    use_container_width=True,
                )
            with right:
                st.plotly_chart(
                    px.bar(
                        strategy_overview.sort_values("mean_improvement_vs_fixed_pct"),
                        x="controller",
                        y="mean_improvement_vs_fixed_pct",
                        color="controller",
                        color_discrete_map=COLOR_MAP,
                        labels={
                            "controller": "Стратегия",
                            "mean_improvement_vs_fixed_pct": "Среднее улучшение к fixed, %",
                        },
                        title="Среднее улучшение относительно fixed",
                    ).update_xaxes(labelalias=CONTROLLER_LABELS),
                    use_container_width=True,
                )

            st.dataframe(
                _format_strategy_overview(strategy_overview),
                use_container_width=True,
                hide_index=True,
            )

            if not ai_vs_actuated.empty:
                st.plotly_chart(
                    px.bar(
                        ai_vs_actuated,
                        x="scenario_title",
                        y="ai_advantage_pct",
                        color="better_controller",
                        color_discrete_map={"ai": "#059669", "actuated": "#2563EB"},
                        labels={
                            "scenario_title": "Сценарий",
                            "ai_advantage_pct": "Преимущество AI, %",
                            "better_controller": "Лучшая стратегия",
                        },
                        title="AI против adaptive: положительное значение означает преимущество AI",
                    ),
                    use_container_width=True,
                )
                st.dataframe(
                    _format_ai_vs_actuated(ai_vs_actuated),
                    use_container_width=True,
                    hide_index=True,
                )

            st.dataframe(
                _format_ranking(scenario_ranking),
                use_container_width=True,
                hide_index=True,
            )

    with runs_tab:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(
                px.box(
                    scenario_runs,
                    x="controller",
                    y="average_wait_seconds",
                    color="controller",
                    points="all",
                    color_discrete_map=COLOR_MAP,
                    labels={
                        "controller": "Стратегия",
                        "average_wait_seconds": "Среднее ожидание, с",
                    },
                    title="Разброс среднего ожидания по seed",
                ).update_xaxes(labelalias=CONTROLLER_LABELS),
                use_container_width=True,
            )
        with right:
            lane_waits = _lane_waits(scenario_runs)
            st.plotly_chart(
                px.bar(
                    lane_waits,
                    x="lane",
                    y="average_wait_seconds",
                    color="controller",
                    barmode="group",
                    color_discrete_map=COLOR_MAP,
                    labels={
                        "lane": "Направление",
                        "average_wait_seconds": "Среднее ожидание, с",
                        "controller": "Стратегия",
                    },
                    title="Ожидание по направлениям",
                ),
                use_container_width=True,
            )

        st.dataframe(
            scenario_runs[
                [
                    "seed",
                    "controller",
                    "vehicles_arrived",
                    "vehicles_departed",
                    "average_wait_seconds",
                    "average_queue_length",
                    "throughput_per_hour",
                    "fairness_index",
                ]
            ].sort_values(["controller", "seed"]),
            use_container_width=True,
            hide_index=True,
        )

    with report_tab:
        report_path = _report_path(result_path)
        if report_path.exists():
            st.markdown(report_path.read_text(encoding="utf-8"))
        else:
            st.warning("Markdown-отчёт для выбранного результата не найден.")


def _select_result_file() -> Path | None:
    generated = sorted(Path("outputs").glob("*_results.json"))
    available = []
    for path in [*DEFAULT_RESULT_FILES, *generated]:
        if path.exists() and path not in available:
            available.append(path)
    if not available:
        return None
    labels = [str(path) for path in available]
    selected = st.sidebar.radio("Файл результатов", labels, index=0)
    return Path(selected)


def _report_path(result_path: Path) -> Path:
    return result_path.with_name(result_path.name.replace("_results.json", "_report.md"))


def _label(controller: str) -> str:
    return CONTROLLER_LABELS.get(controller, controller)


def _format_summary(summary: pd.DataFrame) -> pd.DataFrame:
    columns = {
        "controller": "Стратегия",
        "runs": "Запуски",
        "average_wait_seconds": "Среднее ожидание, с",
        "median_wait_seconds": "Медианное ожидание, с",
        "average_queue_length": "Средняя очередь",
        "throughput_per_hour": "Пропускная способность/час",
        "fairness_index": "Справедливость",
        "wait_improvement_vs_fixed_pct": "Улучшение к fixed, %",
    }
    formatted = summary[list(columns)].rename(columns=columns).copy()
    formatted["Стратегия"] = formatted["Стратегия"].map(_label)
    return formatted


def _format_strategy_overview(overview: pd.DataFrame) -> pd.DataFrame:
    columns = {
        "controller": "Стратегия",
        "scenario_wins": "Победы",
        "mean_rank": "Средний ранг",
        "mean_wait_seconds": "Среднее ожидание, с",
        "mean_improvement_vs_fixed_pct": "Среднее улучшение к fixed, %",
        "mean_queue_length": "Средняя очередь",
        "mean_fairness_index": "Справедливость",
    }
    formatted = overview[list(columns)].rename(columns=columns).copy()
    formatted["Стратегия"] = formatted["Стратегия"].map(_label)
    return formatted


def _format_ai_vs_actuated(frame: pd.DataFrame) -> pd.DataFrame:
    columns = {
        "scenario_title": "Сценарий",
        "ai_wait_seconds": "AI, с",
        "actuated_wait_seconds": "Adaptive, с",
        "ai_delta_seconds": "AI - adaptive, с",
        "ai_advantage_pct": "Преимущество AI, %",
        "better_controller": "Лучше",
    }
    formatted = frame[list(columns)].rename(columns=columns).copy()
    formatted["Лучше"] = formatted["Лучше"].map(_label)
    return formatted


def _format_ranking(ranking: pd.DataFrame) -> pd.DataFrame:
    columns = {
        "scenario_title": "Сценарий",
        "controller": "Стратегия",
        "wait_rank": "Ранг",
        "average_wait_seconds": "Среднее ожидание, с",
        "wait_improvement_vs_fixed_pct": "Улучшение к fixed, %",
    }
    formatted = ranking[list(columns)].rename(columns=columns).copy()
    formatted["Стратегия"] = formatted["Стратегия"].map(_label)
    return formatted


def _lane_waits(runs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, run in runs.iterrows():
        for lane, wait in run["lane_waits"].items():
            rows.append(
                {
                    "controller": run["controller"],
                    "lane": lane,
                    "average_wait_seconds": wait,
                }
            )
    frame = pd.DataFrame(rows)
    return (
        frame.groupby(["controller", "lane"], as_index=False)["average_wait_seconds"]
        .mean()
        .sort_values(["controller", "lane"])
    )


main()
