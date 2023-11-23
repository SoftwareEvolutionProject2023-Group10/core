"""Registers listeners for state change events."""


from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register a switch entity responsible for the lights described by entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, [Platform.SWITCH])
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unregister a music switch entity."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_unload(entry, Platform.SWITCH)
    )
    return True
