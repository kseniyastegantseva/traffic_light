import importlib.util
from pathlib import Path

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
