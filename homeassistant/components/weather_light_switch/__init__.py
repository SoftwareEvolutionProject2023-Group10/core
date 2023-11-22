"""Registers listeners for state change events."""


from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_track_state_change_event,
)
from homeassistant.helpers.typing import ConfigType, EventType

from .const import DOMAIN

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


def weather_to_color(weather) -> tuple[int, int, int] | None:
    """Given the current weather, returns a color representing that weather."""

    if weather.state == "cloudy":
        return (255, 0, 0)

    return None


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register event listeners during startup of Home Assistant."""

    def change_color(color: tuple[int, int, int] | None) -> None:
        if color is None:
            hass.add_job(
                hass.services.async_call,
                "light",
                "turn_off",
                {"entity_id": "light.fake_light"},
            )
        else:
            hass.add_job(
                hass.services.async_call,
                "light",
                "turn_on",
                {
                    "entity_id": "light.fake_light",
                    "rgb_color": color,
                },
            )

    @callback
    async def update_lights_weather(event: EventType[EventStateChangedData]) -> None:
        weather = event.data["new_state"]
        if weather is None:
            return

        color = weather_to_color(weather)
        change_color(color)

    async_track_state_change_event(hass, ["weather.smhi_home"], update_lights_weather)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register a switch entity responsible for the lights described by entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, [Platform.SWITCH])
    )
    return True
