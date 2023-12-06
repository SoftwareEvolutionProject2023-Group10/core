"""File for test weather light service."""
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


async def test_has_weather_service(hass: HomeAssistant):
    """Test weather the service gets registered on setup or not."""
    await async_setup_component(hass, "weather_light_switch", {})

    # Assert if the switch has the service
    assert hass.services.has_service("switch", "weather_service")
