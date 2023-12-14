"""Registers listeners for state change events."""

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

from .const import DOMAIN, WEATHER_SERVICE
from .switch import WeatherLightSwitchEnabledEntity
from .weather_mapping import get_color_for_weather_state

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register event listeners during startup of Home Assistant."""

    async def _weather_service_call(
        switch_entity: WeatherLightSwitchEnabledEntity, call: ServiceCall
    ) -> ServiceResponse:
        if switch_entity.is_on:
            weather_state = hass.states.get(switch_entity.weather_entity_id)

            # Case 1: We take the hardcoded, 2: We get it from the weather entity, 3: We say its windy
            weather_type = (
                call.data["main"]
                if call.data.get("main") is not None
                else weather_state.state
                if weather_state and weather_state.state is not None
                else "windy"
            )

            # Want to add weather_state.attributes.get("temperature") but confused of the weather_type thingy :)
            temperature = None
            brightness = calculate_brightness(temperature)
            hs_color = get_color_for_weather_state(weather_type)

            # We get the switch id, which is send by the `_update_lights_weather()` in switch.py
            switch_entity_id = (
                call.data["entity_id"] if call.data.get("entity_id") is not None else ""
            )

            hass.bus.async_fire(
                "rgb_event",
                {
                    "rgb": hs_color,
                    "condition": str(weather_type),
                    "ent_id": switch_entity_id[0],
                },
            )

            # Call to turn the light on
            for light_id in switch_entity.light_ids:
                await hass.services.async_call(
                    "light",
                    "turn_on",
                    {
                        "entity_id": light_id,
                        "hs_color": hs_color,
                        "brightness": brightness,
                    },
                )

        return {
            "main": str(weather_type),
            "switch_state": switch_entity.state,
            "light_ids": switch_entity.light_ids,
        }

    # Register the service to the 'switch' entity
    hass.data["switch"].async_register_entity_service(
        name=WEATHER_SERVICE,
        func=_weather_service_call,
        schema={
            "main": str,
            "light_id": str,
            "weather_entity_id": str,
        },
        supports_response=SupportsResponse.OPTIONAL,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register a switch entity responsible for the lights described by entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, [Platform.SWITCH])
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unregister a weather switch entity."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_unload(entry, Platform.SWITCH)
    )
    return True


def calculate_brightness(temperature) -> int:
    """Define the brightness base of temperature in the range of 0-100."""
    if temperature is None:
        return 255

    min_temp = -20  # Minimum temperature
    max_temp = 40  # Maximum temperature

    # Normalize the temperature within the range
    normalized_temp = (temperature - min_temp) / (max_temp - min_temp)

    brightness = normalized_temp * 100

    # 0 to 100
    brightness = max(0, min(brightness, 100))

    return int(brightness)
