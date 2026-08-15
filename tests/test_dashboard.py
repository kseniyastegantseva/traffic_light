import importlib.util
from pathlib import Path
from types import SimpleNamespace

from traffic_light.interactive import simulate_interactive_traffic

DASHBOARD_PATH = Path(__file__).parents[1] / "app" / "dashboard.py"
SPEC = importlib.util.spec_from_file_location("traffic_light_dashboard", DASHBOARD_PATH)
assert SPEC and SPEC.loader
DASHBOARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DASHBOARD)


def test_vehicle_markup_contains_one_model_per_input_vehicle():
    queues = {"north": 4, "west": 3, "south": 2, "east": 1}

    markup = DASHBOARD._vehicle_markup(queues)

    assert sum(value.count('class="car-slot"') for value in markup.values()) == 10
    assert all('class="car-model"' in value for value in markup.values())
    assert len(set(markup.values())) == 4


def test_animation_embeds_vehicle_sprite_and_two_dynamic_traffic_lights():
    result = simulate_interactive_traffic({"north": 2, "west": 2, "south": 2, "east": 2})

    html = DASHBOARD._animation_html(result)

    assert "data:image/jpeg;base64," in html
    assert html.count('class="signal-unit"') == 2
    assert "setSignal('north_south',northSouth)" in html
    assert "setSignal('east_west',eastWest)" in html


def test_car_models_scale_down_for_large_queues():
    assert (
        DASHBOARD._car_slot_size(20)
        > DASHBOARD._car_slot_size(50)
        > DASHBOARD._car_slot_size(100)
        > DASHBOARD._car_slot_size(250)
    )


def test_dashboard_rejects_result_from_legacy_session_schema():
    legacy = SimpleNamespace(
        frames=[SimpleNamespace(signal="north_south")],
        phases=[SimpleNamespace(signal="north_south")],
    )
    current = simulate_interactive_traffic({"north": 2, "west": 2, "south": 2, "east": 2})

    assert not DASHBOARD._is_current_result(legacy)
    assert DASHBOARD._is_current_result(current)


def test_phase_table_supports_legacy_phase_objects_without_crashing():
    legacy_phases = [
        SimpleNamespace(
            signal="north_south", started_at=0, duration_seconds=8
        ),
        SimpleNamespace(signal="yellow", started_at=8, duration_seconds=3),
    ]

    rows = DASHBOARD._phase_rows(legacy_phases)

    assert rows[0]["Светофор"] == "Юг–Север"
    assert rows[0]["Сигнал"] == "Зелёный"
    assert rows[1]["Светофор"] == "Смена фазы"
    assert rows[1]["Сигнал"] == "Жёлтый"
