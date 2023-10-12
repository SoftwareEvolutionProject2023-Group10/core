"""Representation of a doorlock."""
from __future__ import annotations

from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ZWaveMeEntity
from .const import ZWaveMePlatform
from .helpers import setup_entry

DEVICE_NAME = ZWaveMePlatform.LOCK


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the lock platform."""
    setup_entry(hass, config_entry, async_add_entities, DEVICE_NAME, ZWaveMeLock)


class ZWaveMeLock(ZWaveMeEntity, LockEntity):
    """Representation of a ZWaveMe lock."""

    @property
    def is_locked(self) -> bool:
        """Return the state of the lock."""
        return self.device.level == "close"

    def unlock(self, **kwargs: Any) -> None:
        """Send command to unlock the lock."""
        self.controller.zwave_api.send_command(self.device.id, "open")

    def lock(self, **kwargs: Any) -> None:
        """Send command to lock the lock."""
        self.controller.zwave_api.send_command(self.device.id, "close")
