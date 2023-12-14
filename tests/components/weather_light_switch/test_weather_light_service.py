"""File for test weather light service."""

from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.weather_light_switch.const import DOMAIN, WEATHER_SERVICE
from homeassistant.components.weather_light_switch.weather_mapping import (
    calculate_brightness,
    get_color_for_weather_state,
    rgb_to_hs,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from tests.common import MockConfigEntry, async_mock_service


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


async def test_temperature():
    """Test that different temperatures corresponds to a certain brightness."""
    test_cases = [
        {"temperature": -40, "expected_brightness": 255},
        {"temperature": -10, "expected_brightness": 212},
        {"temperature": 10, "expected_brightness": 127},
        {"temperature": 40, "expected_brightness": 0},
    ]

    for test_cases in test_cases:
        temperature = test_cases["temperature"]
        expected_brightness = test_cases["expected_brightness"]

        actual_brightness = calculate_brightness(temperature)
        assert actual_brightness == expected_brightness


async def test_weather_changes(hass: HomeAssistant):
    """Test that the weather service is called on weather changes."""
    await async_setup_component(hass, DOMAIN, {})

    WEATHER_ENTITY_ID = "weather.test"
    hass.states.async_set(WEATHER_ENTITY_ID, "sunny")

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        options={"weather_entity_id": WEATHER_ENTITY_ID, "light_ids": []},
    )
    await hass.config_entries.async_add(config_entry)
    SWITCH_ENTITY_ID = "switch.weather_light_switch_enabled"

    weather_service_calls = async_mock_service(hass, SWITCH_DOMAIN, WEATHER_SERVICE)
    await hass.async_block_till_done()

    # If the switch is off, weather changes do not trigger the weather service
    assert hass.states.get(SWITCH_ENTITY_ID).state == STATE_OFF
    hass.states.async_set(WEATHER_ENTITY_ID, "cloudy")
    assert len(weather_service_calls) == 0

    # Turn the switch on (also triggers the weather service)
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: SWITCH_ENTITY_ID},
        blocking=True,
    )
    assert len(weather_service_calls) == 1

    # If the switch is on, weather changes trigger the weather service
    hass.states.async_set(WEATHER_ENTITY_ID, "rainy")
    await hass.async_block_till_done()
    assert len(weather_service_calls) == 2

    # Turn the switch off again
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: SWITCH_ENTITY_ID},
        blocking=True,
    )
    assert len(weather_service_calls) == 2

    # If the switch is off, weather changes do not trigger the weather service
    hass.states.async_set(WEATHER_ENTITY_ID, "sunny")
    await hass.async_block_till_done()
    assert len(weather_service_calls) == 2


async def test_light_change(hass: HomeAssistant):
    """Test that the lights change when the weather is called."""
    await async_setup_component(hass, DOMAIN, {})

    WEATHER_ENTITY_ID = "weather.test"
    WEATHER_CONDITION = "sunny"
    hass.states.async_set(WEATHER_ENTITY_ID, WEATHER_CONDITION)

    LIGHT_ENTITY_ID = "light.test"
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        options={
            "weather_entity_id": WEATHER_ENTITY_ID,
            "light_ids": [LIGHT_ENTITY_ID],
        },
    )

    await hass.config_entries.async_add(config_entry)
    SWITCH_ENTITY_ID = "switch.weather_light_switch_enabled"

    light_service_calls = async_mock_service(hass, LIGHT_DOMAIN, SERVICE_TURN_ON)
    await hass.async_block_till_done()

    # WEATHER_SERVICE does nothing if the switch is turned off
    assert hass.states.get(SWITCH_ENTITY_ID).state == STATE_OFF
    result = await hass.services.async_call(
        SWITCH_DOMAIN,
        WEATHER_SERVICE,
        {ATTR_ENTITY_ID: SWITCH_ENTITY_ID},
        blocking=True,
        return_response=True,
    )
    await hass.async_block_till_done()
    assert len(light_service_calls) == 0

    # Turn the switch on (WEATHER_SERVICE is also called)
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: SWITCH_ENTITY_ID},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(SWITCH_ENTITY_ID).state == STATE_ON
    assert len(light_service_calls) == 1

    # WEATHER_SERVICE changes the light if the switch is turned on
    result = await hass.services.async_call(
        SWITCH_DOMAIN,
        WEATHER_SERVICE,
        {ATTR_ENTITY_ID: SWITCH_ENTITY_ID},
        blocking=True,
        return_response=True,
    )
    await hass.async_block_till_done()
    assert len(light_service_calls) == 2
    assert result["main"] == WEATHER_CONDITION
    assert result["switch_state"] == STATE_ON
    assert result["light_ids"] == [LIGHT_ENTITY_ID]


async def test_config_entry_update(hass: HomeAssistant):
    """Test that the switch updates when the config entry is changed."""
    await async_setup_component(hass, DOMAIN, {})

    WEATHER_ENTITY_ID = "weather.test1"
    LIGHT_ENTITY_ID = "light.test1"
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        options={
            "weather_entity_id": WEATHER_ENTITY_ID,
            "light_ids": [LIGHT_ENTITY_ID],
        },
    )

    await hass.config_entries.async_add(config_entry)
    SWITCH_ENTITY_ID = "switch.weather_light_switch_enabled"

    weather_service_calls = async_mock_service(hass, SWITCH_DOMAIN, WEATHER_SERVICE)
    await hass.async_block_till_done()

    # Change the config entry
    WEATHER_ENTITY_ID = "weather.test2"
    LIGHT_ENTITY_ID = "light.test2"
    hass.config_entries.async_update_entry(
        config_entry,
        options={
            "weather_entity_id": WEATHER_ENTITY_ID,
            "light_ids": [LIGHT_ENTITY_ID],
        },
    )
    await hass.async_block_till_done()
    assert hass.states.get(SWITCH_ENTITY_ID).state == STATE_OFF
    assert len(weather_service_calls) == 0

    # Turn the switch on
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: SWITCH_ENTITY_ID},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(SWITCH_ENTITY_ID).state == STATE_ON
    assert len(weather_service_calls) == 1

    # Change the config entry
    WEATHER_ENTITY_ID = "weather.test3"
    LIGHT_ENTITY_ID = "light.test3"
    hass.config_entries.async_update_entry(
        config_entry,
        options={
            "weather_entity_id": WEATHER_ENTITY_ID,
            "light_ids": [LIGHT_ENTITY_ID],
        },
    )

    await hass.async_block_till_done()
    assert hass.states.get(SWITCH_ENTITY_ID).state == STATE_ON
    assert len(weather_service_calls) == 2
