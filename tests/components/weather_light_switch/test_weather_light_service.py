"""File for test weather light service."""

from homeassistant.components.weather_light_switch.weather_mapping import (
    get_color_for_weather_state,
    rgb_to_hs,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


async def test_has_weather_service(hass: HomeAssistant):
    """Test weather the service gets registered on setup or not."""
    await async_setup_component(hass, "weather_light_switch", {})

    # Assert if the switch has the service
    assert hass.services.has_service("switch", "weather_service")


async def test_colors():
    """Test that different weather types corresponds to certain colors."""
    test_cases = [
        {"weather_state": "windy", "expected_color": (255, 69, 0)},
        {"weather_state": "rainy", "expected_color": (30, 144, 255)},
        {"weather_state": "cloudy", "expected_color": (0, 128, 128)},
        {"weather_state": "sunny", "expected_color": (255, 255, 0)},
    ]

    for test_cases in test_cases:
        weather_state = test_cases["weather_state"]
        expected_color = test_cases["expected_color"]
        expected_color_hs = rgb_to_hs(expected_color)

        actual_color = get_color_for_weather_state(weather_state)
        assert actual_color == expected_color_hs


async def test_invalid_weather_state():
    """Test behavior for an invalid weather state."""
    invalid_state = "unknown_weather_state"
    expected_default_color = (0, 0, 0)  # Assuming default color for unknown state

    actual_color = get_color_for_weather_state(invalid_state)
    assert actual_color == rgb_to_hs(expected_default_color)
