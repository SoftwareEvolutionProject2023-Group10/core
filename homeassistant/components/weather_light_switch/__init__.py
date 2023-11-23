"""Registers listeners for state change events."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import COLOR_MAP, DOMAIN, OFF, WINDY
from .switch import WeatherLightSwitchEnabledEntity

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register event listeners during startup of Home Assistant."""

    async def _weather_service_call(
        switch_entity: WeatherLightSwitchEnabledEntity, call: ServiceCall
    ) -> ServiceResponse:
        if switch_entity.is_on:
            weather_state = hass.states.get(switch_entity.weather_entity_id)
            weather_type = (
                call.data["main"]
                if call.data.get("main") is not None
                else weather_state.state
                if weather_state and weather_state.state is not None
                else WINDY
            )

            rgb_color = COLOR_MAP.get(weather_type, OFF)

            switch_entity_id = (
                call.data["entity_id"] if call.data.get("entity_id") is not None else ""
            )

            hass.bus.async_fire(
                "rgb_event",
                {
                    "rgb": rgb_color,
                    "condition": str(weather_type),
                    "ent_id": switch_entity_id[0],
                },
            )

            for light_id in switch_entity.light_ids:
                await hass.services.async_call(
                    "light",
                    "turn_on",
                    {
                        "entity_id": light_id,
                        "rgb_color": rgb_color,
                    },
                )
        else:
            for light_id in switch_entity.light_ids:
                await hass.services.async_call(
                    "light",
                    "turn_on",
                    {
                        "entity_id": light_id,
                    },
                )
        return {
            "switch_state": switch_entity.state,
            "light_ids": switch_entity.light_ids,
        }

    hass.data["switch"].async_register_entity_service(
        name="weather_service",
        func=_weather_service_call,
        schema={
            "main": str,
            "light_id": str,
            "weather_entity_id": str,
        },
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register a switch entity responsible for the lights described by entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, [Platform.SWITCH])
    )
    return True
