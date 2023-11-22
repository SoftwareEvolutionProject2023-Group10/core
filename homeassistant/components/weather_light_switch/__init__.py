"""Registers listeners for state change events."""

import voluptuous as vol

from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_track_state_change_event,
)
from homeassistant.helpers.typing import ConfigType, EventType

from .const import ATTR_SIM_LIGHT_ENTITY, BLACK, COLOR_MAP, DOMAIN, WINDY

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

    async def _weather_service_call(call: ServiceCall) -> ServiceResponse:
        # FM:See if the weather_feature is on
        # If is off -> Act like normal light --> toggle
        # If is on -> Set the light based on weather

        # FM:Choose from the selected light entities that is selected in the switcher. Also do loop for all chosen ones
        weather_ent_id = "weather.smhi_weather"
        weather_state = hass.states.get(weather_ent_id)

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
            },
        )

        return {"main": str(weather_type), "rgb": str(rgb_color)}

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

    @callback
    async def update_lights_weather(event: EventType[EventStateChangedData]) -> None:
        weather = event.data["new_state"]
        if weather is None:
            return

        color = weather_to_color(weather)
        change_color(color)

    async_track_state_change_event(hass, ["weather.smhi_home"], update_lights_weather)
    return True
