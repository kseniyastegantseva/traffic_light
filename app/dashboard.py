from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Intelligent Traffic Light", layout="wide")
st.title("Intelligent Traffic Light Control")

results_path = Path("outputs/compare_results.json")

if not results_path.exists():
    st.info("Run `traffic-sim compare --config configs/experiment.yaml` to generate experiment data.")
    st.stop()

payload = json.loads(results_path.read_text(encoding="utf-8"))
runs = pd.DataFrame(payload["runs"])
summary = pd.DataFrame(payload["summary"])

st.subheader("Experiment Summary")
st.dataframe(summary, use_container_width=True)

left, right = st.columns(2)
with left:
    st.plotly_chart(
        px.bar(
            summary,
            x="controller",
            y="average_wait_seconds",
            error_y="wait_95ci_half_width",
            title="Average wait time by controller",
        ),
        use_container_width=True,
    )

with right:
    st.plotly_chart(
        px.bar(
            summary,
            x="controller",
            y="throughput_per_hour",
            title="Throughput by controller",
        ),
        use_container_width=True,
    )

st.subheader("Run Distribution")
st.plotly_chart(
    px.box(
        runs,
        x="controller",
        y="average_wait_seconds",
        points="all",
        title="Wait-time distribution across seeds",
    ),
    use_container_width=True,
)
