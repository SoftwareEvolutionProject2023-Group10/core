"""Representation of a cover."""
from __future__ import annotations

from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ZWaveMeEntity
from .const import ZWaveMePlatform
from .helpers import setup_entry

DEVICE_NAME = ZWaveMePlatform.COVER


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the cover platform."""
    setup_entry(hass, config_entry, async_add_entities, DEVICE_NAME, ZWaveMeCover)


class ZWaveMeCover(ZWaveMeEntity, CoverEntity):
    """Representation of a ZWaveMe Multilevel Cover."""

    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
        | CoverEntityFeature.STOP
    )

    def close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        self.controller.zwave_api.send_command(self.device.id, "exact?level=0")

    def open_cover(self, **kwargs: Any) -> None:
        """Open cover."""
        self.controller.zwave_api.send_command(self.device.id, "exact?level=99")

    def set_cover_position(self, **kwargs: Any) -> None:
        """Update the current value."""
        value = kwargs[ATTR_POSITION]
        self.controller.zwave_api.send_command(
            self.device.id, f"exact?level={str(min(value, 99))}"
        )

    def stop_cover(self, **kwargs: Any) -> None:
        """Stop cover."""
        self.controller.zwave_api.send_command(self.device.id, "stop")

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open.

        Allow small calibration errors (some devices after a long time
        become not well calibrated).
        """
        if self.device.level > 95:
            return 100

        return self.device.level

    @property
    def is_closed(self) -> bool | None:
        """Return true if cover is closed.

        None is unknown.

        Allow small calibration errors (some devices after a long time
        become not well calibrated).
        """
        if self.device.level is None:
            return None

        return self.device.level < 5
