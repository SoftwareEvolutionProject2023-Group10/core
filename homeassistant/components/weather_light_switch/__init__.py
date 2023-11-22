"""Registers listeners for state change events."""

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import ATTR_SIM_LIGHT_ENTITY, BLACK, COLOR_MAP, DOMAIN, WINDY

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register event listeners during startup of Home Assistant."""

    async def _weather_service_call(call: ServiceCall) -> ServiceResponse:
        # FM:See if the weather_feature is on
        # If is off -> Act like normal light --> toggle
        # If is on -> Set the light based on weather

        # FM:Choose from the selected light entities that is selected in the switcher. Also do loop for all chosen ones
        weather_ent_id = "weather.smhi_weather"
        weather_state = hass.states.get(weather_ent_id)

        temperature = None
        brightness = calculate_brightness(temperature)

        weather_type = (
            call.data["main"]
            if call.data.get("main") is not None
            else weather_state.state
            if weather_state and weather_state.state is not None
            else WINDY
        )

        # Define the RGB color based on your weather type (replace this with your logic)
        rgb_color = COLOR_MAP.get(weather_type, BLACK)

        # Fire custom event
        hass.bus.async_fire(
            "rgb_event", {"rgb": rgb_color, "condition": str(weather_type)}
        )

        # Call to turn the light on
        await hass.services.async_call(
            "light",
            "turn_on",
            {
                "entity_id": ATTR_SIM_LIGHT_ENTITY,
                "rgb_color": rgb_color,
                "brightness": brightness,
            },
        )

        return {
            "main": str(weather_type),
            "rgb": str(rgb_color),
            "brightness": brightness,
        }

    hass.services.async_register(
        domain=DOMAIN,
        service="weather_service",
        service_func=_weather_service_call,
        schema=vol.Schema(
            {
                vol.Optional("main"): str,
            }
        ),
        supports_response=SupportsResponse.OPTIONAL,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register a switch entity responsible for the lights described by entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, [Platform.SWITCH])
    )
    return True


def calculate_brightness(temperature) -> int:
    """Define the brightness base of temperature in the range of 0-100."""
    min_temp = -20  # Minimum temperature
    max_temp = 40  # Maximum temperature

    # Normalize the temperature within the range
    normalized_temp = (temperature - min_temp) / (max_temp - min_temp)

    brightness = normalized_temp * 100

    # 0 to 100
    brightness = max(0, min(brightness, 100))

    return int(brightness)
