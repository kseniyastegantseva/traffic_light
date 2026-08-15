from __future__ import annotations

import json
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

from traffic_light.config import LaneName
from traffic_light.interactive import InteractiveSimulationResult, simulate_interactive_traffic

LANE_LABELS = {
    "north": "Север",
    "west": "Запад",
    "south": "Юг",
    "east": "Восток",
}


def main() -> None:
    st.set_page_config(page_title="Интеллектуальный светофор", layout="wide")
    _apply_styles()

    st.title("Интеллектуальный светофор")
    st.caption("Введите число автомобилей на каждом подходе и запустите управление фазами.")

    with st.form("traffic-input"):
        columns = st.columns(4)
        defaults = {"north": 12, "west": 5, "south": 10, "east": 4}
        queues: dict[LaneName, int] = {}
        for column, lane in zip(columns, LANE_LABELS, strict=True):
            with column:
                queues[lane] = st.number_input(
                    LANE_LABELS[lane],
                    min_value=0,
                    max_value=250,
                    value=defaults[lane],
                    step=1,
                )
        submitted = st.form_submit_button(
            "Запустить симуляцию", type="primary", width="stretch"
        )

    if submitted or "interactive_result" not in st.session_state:
        st.session_state.interactive_result = simulate_interactive_traffic(queues)

    result: InteractiveSimulationResult = st.session_state.interactive_result
    _scenario_banner(result)
    _metrics(result)

    left, right = st.columns([1.55, 1], gap="large")
    with left:
        st.subheader("Работа перекрёстка")
        st.iframe(_animation_html(result), height=690, width="stretch")
    with right:
        st.subheader("Как меняется очередь")
        st.plotly_chart(_queue_chart(result), width="stretch", config={"displayModeBar": False})
        st.caption(
            "Линия показывает, сколько автомобилей ещё ожидает проезда. "
            "Снижение до нуля означает завершение работы алгоритма."
        )
        _phase_table(result)


def _scenario_banner(result: InteractiveSimulationResult) -> None:
    st.markdown(
        f"""
        <div class="scenario-banner">
          <div><span class="eyebrow">ОПРЕДЕЛЁННЫЙ СЦЕНАРИЙ</span>
          <strong>{escape(result.scenario.title)}</strong></div>
          <p>{escape(result.scenario.description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _metrics(result: InteractiveSimulationResult) -> None:
    total = sum(result.initial_queues.values())
    columns = st.columns(4)
    columns[0].metric("Автомобилей", total)
    columns[1].metric("Время работы", _format_seconds(result.total_time_seconds))
    columns[2].metric("Переключений фаз", result.switches)
    columns[3].metric("Проехало", result.departed)


def _queue_chart(result: InteractiveSimulationResult):
    rows = [
        {
            "Время, с": frame.second,
            "Осталось автомобилей": sum(frame.queues.values()),
        }
        for frame in result.frames
    ]
    frame = pd.DataFrame(rows)
    figure = px.line(
        frame,
        x="Время, с",
        y="Осталось автомобилей",
        markers=result.total_time_seconds <= 30,
    )
    figure.update_traces(line_color="#166534", line_width=3)
    figure.update_layout(
        height=320,
        margin={"l": 10, "r": 10, "t": 16, "b": 10},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        hovermode="x unified",
    )
    figure.update_yaxes(rangemode="tozero", gridcolor="#e5e7eb")
    figure.update_xaxes(gridcolor="#f3f4f6")
    return figure


def _phase_table(result: InteractiveSimulationResult) -> None:
    st.subheader("Распределение времени")
    north, east = st.columns(2)
    north.metric("Светофор Юг–Север", _format_seconds(result.north_south_green_seconds))
    east.metric("Светофор Восток–Запад", _format_seconds(result.east_west_green_seconds))
    if result.phases:
        axis_labels = {"north_south": "Юг–Север", "east_west": "Восток–Запад"}
        color_labels = {"green": "Зелёный", "yellow": "Жёлтый", "red": "Красный"}
        phase_rows = [
            {
                "Светофор": axis_labels[phase.axis],
                "Сигнал": color_labels[phase.color],
                "Начало": f"{phase.started_at} с",
                "Длительность": f"{phase.duration_seconds} с",
            }
            for phase in result.phases
        ]
        st.dataframe(phase_rows, hide_index=True, width="stretch", height=220)


def _animation_html(result: InteractiveSimulationResult) -> str:
    frames = [frame.to_dict() for frame in result.frames]
    initial = result.initial_queues
    car_markup = {
        lane: "".join('<span class="car"></span>' for _ in range(count))
        for lane, count in initial.items()
    }
    return f"""
<!doctype html>
<html lang="ru">
<head><meta charset="utf-8"><style>
* {{ box-sizing: border-box; }}
body {{ margin:0; font-family:Inter,Arial,sans-serif; color:#17211b; background:#fff; }}
.sim {{ border:1px solid #d9e1dc; border-radius:8px; overflow:hidden; background:#f5f7f5; }}
.toolbar {{ height:58px; display:flex; align-items:center; gap:10px; padding:10px 14px; background:#fff; border-bottom:1px solid #d9e1dc; }}
button,select {{ height:36px; border:1px solid #c9d3cc; background:#fff; border-radius:6px; padding:0 12px; font-weight:650; color:#17211b; cursor:pointer; }}
button.primary {{ background:#166534; border-color:#166534; color:#fff; }}
.status {{ margin-left:auto; text-align:right; }}
.status strong {{ display:block; font-size:16px; }} .status span {{ font-size:12px; color:#637068; }}
.scene {{ position:relative; height:555px; background:#dce8dc; overflow:hidden; }}
.road-v {{ position:absolute; width:30%; height:100%; left:35%; top:0; background:#414844; border-left:3px solid #f8faf9; border-right:3px solid #f8faf9; }}
.road-h {{ position:absolute; width:100%; height:30%; left:0; top:35%; background:#414844; border-top:3px solid #f8faf9; border-bottom:3px solid #f8faf9; }}
.center {{ position:absolute; width:30%; height:30%; left:35%; top:35%; background:#4b534e; z-index:2; }}
.lane {{ position:absolute; z-index:4; display:flex; gap:3px; align-content:flex-start; overflow:hidden; }}
.lane.north {{ width:27%; height:32%; left:6%; top:2%; flex-wrap:wrap; align-items:flex-start; }}
.lane.south {{ width:27%; height:32%; right:6%; bottom:2%; flex-wrap:wrap-reverse; align-items:flex-end; }}
.lane.west {{ width:32%; height:27%; left:2%; bottom:6%; flex-wrap:wrap-reverse; align-items:flex-end; }}
.lane.east {{ width:32%; height:27%; right:2%; top:6%; flex-wrap:wrap; align-items:flex-start; }}
.car {{ display:block; width:14px; height:8px; border-radius:2px; background:#e2553d; border:1px solid #883626; box-shadow:0 1px 1px #0003; transition:opacity .16s,transform .16s; }}
.north .car,.south .car {{ width:8px; height:14px; background:#276fbf; border-color:#194d86; }}
.car.passed {{ opacity:0; transform:scale(.3); }}
.lane-label {{ position:absolute; z-index:6; padding:5px 8px; background:#ffffffed; border:1px solid #cad4cd; border-radius:5px; font-size:12px; font-weight:700; }}
.label-north {{ left:8px; top:8px; }} .label-south {{ right:8px; bottom:8px; }}
.label-west {{ left:8px; bottom:8px; }} .label-east {{ right:8px; top:8px; }}
.signal-panel {{ position:absolute; z-index:8; left:50%; top:50%; transform:translate(-50%,-50%); width:190px; display:grid; gap:6px; }}
.signal-unit {{ display:grid; grid-template-columns:82px 1fr; align-items:center; gap:5px; padding:5px; border-radius:5px; background:#f7faf8; border:1px solid #cbd5ce; }}
.signal-name {{ font-size:10px; line-height:1.1; font-weight:800; color:#253229; text-align:center; }}
.housing {{ display:flex; justify-content:center; gap:5px; padding:5px; border-radius:5px; background:#202622; box-shadow:0 2px 4px #0005; }}
.bulb {{ width:16px; height:16px; border-radius:50%; background:#47504a; border:1px solid #111; }}
.bulb.active.red {{ background:#dc2626; box-shadow:0 0 9px #dc2626; }}
.bulb.active.yellow {{ background:#facc15; box-shadow:0 0 9px #facc15; }}
.bulb.active.green {{ background:#22c55e; box-shadow:0 0 9px #22c55e; }}
.phase-label {{ padding:3px 5px; border-radius:4px; background:#202622e8; color:#fff; text-align:center; font-size:10px; font-weight:750; }}
.progress {{ height:7px; background:#e6ebe8; }} .progress>div {{ height:100%; background:#166534; width:0; transition:width .2s; }}
.legend {{ padding:10px 14px; font-size:12px; color:#637068; background:#fff; border-top:1px solid #d9e1dc; }}
@media(max-width:700px) {{ .scene {{ height:470px; }} .car {{ width:10px;height:6px }} .north .car,.south .car {{width:6px;height:10px}} }}
</style></head>
<body><div class="sim">
  <div class="toolbar">
    <button id="play" class="primary">Пауза</button><button id="reset">Сначала</button>
    <select id="speed" aria-label="Скорость"><option value="1">1x</option><option value="2">2x</option><option value="4" selected>4x</option><option value="8">8x</option></select>
    <div class="status"><strong id="clock">0 с / {result.total_time_seconds} с</strong><span id="remaining">Ожидает: {sum(initial.values())}</span></div>
  </div>
  <div class="progress"><div id="progress"></div></div>
  <div class="scene">
    <div class="road-v"></div><div class="road-h"></div><div class="center"></div>
    <div class="lane north" id="cars-north">{car_markup['north']}</div>
    <div class="lane west" id="cars-west">{car_markup['west']}</div>
    <div class="lane south" id="cars-south">{car_markup['south']}</div>
    <div class="lane east" id="cars-east">{car_markup['east']}</div>
    <div class="lane-label label-north">Север: <span id="count-north">{initial['north']}</span></div>
    <div class="lane-label label-west">Запад: <span id="count-west">{initial['west']}</span></div>
    <div class="lane-label label-south">Юг: <span id="count-south">{initial['south']}</span></div>
    <div class="lane-label label-east">Восток: <span id="count-east">{initial['east']}</span></div>
    <div class="signal-panel">
      <div class="signal-unit" id="signal-north_south">
        <span class="signal-name">ЮГ–СЕВЕР</span>
        <div class="housing"><span class="bulb red" data-color="red"></span><span class="bulb yellow" data-color="yellow"></span><span class="bulb green" data-color="green"></span></div>
      </div>
      <div class="signal-unit" id="signal-east_west">
        <span class="signal-name">ВОСТОК–ЗАПАД</span>
        <div class="housing"><span class="bulb red" data-color="red"></span><span class="bulb yellow" data-color="yellow"></span><span class="bulb green" data-color="green"></span></div>
      </div>
      <div class="phase-label" id="phase-label"></div>
    </div>
  </div>
  <div class="legend">Два светофора работают взаимоисключающе: Юг–Север управляет вертикальным потоком, Восток–Запад — горизонтальным. Один шаг равен одной секунде модели.</div>
</div>
<script>
const frames={json.dumps(frames, ensure_ascii=False)};
const initial={json.dumps(initial)};
let index=0,playing=true,timer;
const lanes=['north','west','south','east'];
function paint(){{
  const frame=frames[index];if(!frame)return;
  lanes.forEach(lane=>{{
    document.getElementById('count-'+lane).textContent=frame.queues[lane];
    const cars=document.querySelectorAll('#cars-'+lane+' .car');
    cars.forEach((car,i)=>car.classList.toggle('passed',i>=frame.queues[lane]));
  }});
  function setSignal(axis,color){{
    document.querySelectorAll('#signal-'+axis+' .bulb').forEach(bulb=>bulb.classList.toggle('active',bulb.dataset.color===color));
  }}
  const northSouth=frame.signals.north_south;
  const eastWest=frame.signals.east_west;
  setSignal('north_south',northSouth);setSignal('east_west',eastWest);
  let label='Оба светофора: красный';
  if(northSouth==='green')label='Проезд: Юг–Север';
  if(eastWest==='green')label='Проезд: Восток–Запад';
  if(northSouth==='yellow')label='Юг–Север завершает фазу';
  if(eastWest==='yellow')label='Восток–Запад завершает фазу';
  let nextChange=index+1;
  while(nextChange<frames.length && frames[nextChange].signals.north_south===northSouth && frames[nextChange].signals.east_west===eastWest)nextChange++;
  const phaseLeft=Math.max(1,nextChange-index);
  document.getElementById('phase-label').textContent=label+' · ещё '+phaseLeft+' с';
  document.getElementById('clock').textContent=frame.second+' с / {result.total_time_seconds} с';
  document.getElementById('remaining').textContent='Ожидает: '+lanes.reduce((s,l)=>s+frame.queues[l],0)+' · Проехало: '+frame.departed;
  document.getElementById('progress').style.width=(100*(index+1)/frames.length)+'%';
  if(index>=frames.length-1){{playing=false;document.getElementById('play').textContent='Повторить';clearInterval(timer);}}
}}
function startTimer(){{clearInterval(timer);if(playing)timer=setInterval(()=>{{if(index<frames.length-1){{index++;paint();}}}},1000/Number(document.getElementById('speed').value));}}
document.getElementById('play').onclick=()=>{{if(index>=frames.length-1){{index=0;playing=false;}}playing=!playing;document.getElementById('play').textContent=playing?'Пауза':'Продолжить';paint();startTimer();}};
document.getElementById('reset').onclick=()=>{{index=0;playing=true;document.getElementById('play').textContent='Пауза';paint();startTimer();}};
document.getElementById('speed').onchange=startTimer;
paint();startTimer();
</script></body></html>
"""


def _format_seconds(seconds: int) -> str:
    minutes, remainder = divmod(seconds, 60)
    return f"{minutes} мин {remainder} с" if minutes else f"{remainder} с"


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width:1280px;padding-top:2rem;padding-bottom:3rem;}
        h1,h2,h3 {letter-spacing:0 !important;}
        .scenario-banner {display:flex;align-items:center;justify-content:space-between;gap:24px;
          margin:18px 0;padding:16px 18px;border-left:5px solid #166534;background:#f2f7f3;}
        .scenario-banner strong {display:block;font-size:19px;margin-top:3px;}
        .scenario-banner p {margin:0;max-width:560px;color:#4b5d52;}
        .eyebrow {font-size:11px;font-weight:800;color:#166534;}
        div[data-testid="stMetric"] {border-top:2px solid #d7e2da;padding-top:12px;}
        div[data-testid="stForm"] {border-radius:8px;border-color:#d7e2da;}
        @media(max-width:700px) {.scenario-banner {display:block}.scenario-banner p {margin-top:8px}}
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
