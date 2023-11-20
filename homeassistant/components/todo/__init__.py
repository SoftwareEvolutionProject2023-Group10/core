"""Support for the Philips Hue system."""


import logging

from weather_mapping import get_color_for_weather_state

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_track_state_change_event,
)
from homeassistant.helpers.typing import ConfigType, EventType

_LOGGER = logging.getLogger(__name__)


def weather_to_color(weather) -> tuple[int, int, int] | None:
    """Calculate and return the color based on the weather state."""
    _LOGGER.debug("calculating light color based on weather")

    return get_color_for_weather_state(weather.state)


def song_to_color(song_title: str) -> tuple[int, int, int] | None:
    """Calculate and return the color based on the song title."""
    _LOGGER.debug("Calculating light color based on song_title: %s", song_title)

    if song_title == "Mirchi":
        return (255, 0, 0)
    return None


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Async setup for change_color."""

    def change_color(color: tuple[int, int, int] | None) -> None:
        """Change the color of the light based on the provided color tuple."""
        _LOGGER.debug("Changing color to: %s", color)
        if color is None:
            hass.add_job(
                hass.services.async_call,
                "light",
                "turn_off",
                {"entity_id": config["todo"]["light_id"]},
            )
        else:
            hass.add_job(
                hass.services.async_call,
                "light",
                "turn_on",
                {
                    "entity_id": config["todo"]["light_id"],
                    "rgb_color": color,
                    "brightness": 60,
                },
            )

    @callback
    def update_lights_weather(event: EventType[EventStateChangedData]) -> None:
        """Update light colors based on weather changes."""
        weather = event.data["new_state"]
        color = weather_to_color(weather)
        change_color(color)

    @callback
    def update_lights_music(event: EventType[EventStateChangedData]) -> None:
        """Update light colors based on music changes."""
        _LOGGER.debug("Music changed")
        if event.data["new_state"] is None:
            color = None
        else:
            song = event.data["new_state"].attributes.get("media_title")
            color = song_to_color(song) if song is not None else None
        change_color(color)

    async_track_state_change_event(
        hass, ["weather.forecast_home"], update_lights_weather
    )
    async_track_state_change_event(hass, ["media_player.mpd"], update_lights_music)

    return True
