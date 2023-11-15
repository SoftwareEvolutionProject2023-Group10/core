"""Support for the Philips Hue system."""

from datetime import datetime, timedelta
from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

def weather_to_color(weather) -> str | None:
    print("calculating light color")
    print(weather.state)
    if weather.state == "cloudy":
        return (255, 0, 0)
    else:
        return None

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async def update_lights(time: datetime) -> None:
        weather = hass.states.get("weather.forecast_home")

        color = weather_to_color(weather)
        print(color)

        if color is None:
            await hass.services.async_call(
                "light",
                "turn_off",
                {"entity_id": "light." + config["todo"]["light_id"]}
            )
        else:
            await hass.services.async_call(
                "light",
                "turn_on",
                {"entity_id": "light." + config["todo"]["light_id"], "rgb_color": color}
            )
        pass

    async_track_time_interval(hass, update_lights, timedelta(seconds=15))

    print("----------------------------- async_setup()")
    return True
