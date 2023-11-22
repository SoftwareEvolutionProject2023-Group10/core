"""Support for enabling and disabling the weather and music syncing."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


class WeatherLightSwitchEnabledEntity(SwitchEntity):
    """Enabled state of a light switcher."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_is_on = True

    def __init__(
        self,
        config_entry,
    ) -> None:
        """Initialize the entity."""
        self._attr_unique_id = config_entry.entry_id
        self.entity_id = f"{DOMAIN}.weather_light_switch_enabled"
        self._light_ids = config_entry.data.get("light_ids", [])

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._attr_is_on = False


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up light entities."""
    async_add_entities(
        [
            WeatherLightSwitchEnabledEntity(config_entry),
        ]
    )
