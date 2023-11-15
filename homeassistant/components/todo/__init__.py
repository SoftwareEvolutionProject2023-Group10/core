"""Support for the Philips Hue system."""

from datetime import datetime, timedelta

from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event, EventStateChangedData
from homeassistant.helpers.typing import ConfigType, EventType


def weather_to_color(weather) -> str | None:
    print("calculating light color based on weather")
    print(weather.state)
    if weather.state == "cloudy":
        return (255, 0, 0)
    else:
        return None

def song_to_color(song_title: str) -> str | None:
    print("calculating light color based on song_title")
    print(song_title)
    if song_title == "Mirchi":
        return (255, 0, 0)
    else:
        return None


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    def change_color(color: tuple[int, int, int] | None) -> None:
        print(color)
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
                },
            )

    @callback
    def update_lights_weather(event: EventType[EventStateChangedData]) -> None:
        weather = event.data["new_state"]
        color = weather_to_color(weather)
        change_color(color)

    @callback
    def update_lights_music(event: EventType[EventStateChangedData]) -> None:
        print("music changed")
        song = event.data["new_state"].attributes.get("media_title")
        if song is None:
            color = None
        else:
            color = song_to_color(song)
        change_color(color)

    async_track_state_change_event(hass, ["weather.forecast_home"], update_lights_weather)
    async_track_state_change_event(hass, ["media_player.mpd"], update_lights_music)

    return True
