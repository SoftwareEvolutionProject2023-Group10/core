"""File for test weather light service."""

from homeassistant import config_entries
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.weather_light_switch import async_setup_entry
from homeassistant.components.weather_light_switch.const import DOMAIN, WEATHER_SERVICE
from homeassistant.components.weather_light_switch.weather_mapping import (
    get_color_for_weather_state,
    rgb_to_hs,
)
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_ON, STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from tests.common import async_mock_service


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


async def test_weather_changes(hass: HomeAssistant):
    """Test that the weather service is called on weather changes."""
    await async_setup_component(hass, DOMAIN, {})

    WEATHER_ENTITY_ID = "weather.test"
    hass.states.async_set(WEATHER_ENTITY_ID, "sunny")

    config_entry = config_entries.ConfigEntry(
        1,
        DOMAIN,
        "Mock Title",
        {},
        "test",
        options={"weather_entity_id": WEATHER_ENTITY_ID, "light_ids": []},
    )
    await async_setup_entry(hass, config_entry)
    SWITCH_ENTITY_ID = "switch.weather_light_switch_enabled"

    weather_service_calls = async_mock_service(hass, SWITCH_DOMAIN, WEATHER_SERVICE)
    await hass.async_block_till_done()

    assert hass.states.get(SWITCH_ENTITY_ID).state == STATE_OFF
    hass.states.async_set(WEATHER_ENTITY_ID, "cloudy")
    assert len(weather_service_calls) == 0

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: SWITCH_ENTITY_ID},
        blocking=True,
    )
    assert len(weather_service_calls) == 1

    hass.states.async_set(WEATHER_ENTITY_ID, "rainy")
    await hass.async_block_till_done()
    assert len(weather_service_calls) == 2
