"""Support for enabling and disabling the weather and music syncing."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_track_state_change_event,
)
from homeassistant.helpers.typing import EventType

from .const import DOMAIN


def weather_to_color(weather) -> tuple[int, int, int] | None:
    """Given the current weather, returns a color representing that weather."""

    if weather.state == "cloudy":
        return (255, 0, 0)

    return None


class WeatherLightSwitchEnabledEntity(SwitchEntity):
    """Enabled state of a light switcher."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_is_on = False
    _remove_weather_listener: CALLBACK_TYPE | None = None

    def __init__(self, config_entry) -> None:
        """Initialize the entity."""
        self._attr_unique_id = config_entry.entry_id
        self.entity_id = f"{DOMAIN}.weather_light_switch_enabled"
        self._weather_entity_id = config_entry.options["weather_entity_id"]
        self._light_ids = config_entry.options["light_ids"]

    @callback
    async def _update_lights_weather(
        self, event: EventType[EventStateChangedData]
    ) -> None:
        """Call back for update of the weather."""

        await self.hass.services.async_call(
            "switch",
            "weather_service",
            {"entity_id": self.entity_id, "weather_entity_id": self._weather_entity_id},
        )

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._attr_is_on = True
        self._remove_weather_listener = async_track_state_change_event(
            self.hass, [self._weather_entity_id], self._update_lights_weather
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._attr_is_on = False
        if self._remove_weather_listener is not None:
            self._remove_weather_listener()
            self._remove_weather_listener = None

    @property
    def weather_entity_id(self):
        """Getter for weather_entity_id."""
        return self._weather_entity_id

    @property
    def light_ids(self):
        """Getter to get all light ids."""
        return self._light_ids


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up light entities."""
    async_add_entities([WeatherLightSwitchEnabledEntity(config_entry)])
