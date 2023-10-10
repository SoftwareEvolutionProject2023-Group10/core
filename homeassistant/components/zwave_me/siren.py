"""Representation of a sirenBinary."""
from typing import Any

from homeassistant.components.siren import SirenEntity, SirenEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ZWaveMeEntity
from .const import ZWaveMePlatform
from .helpers import setup_entry

DEVICE_NAME = ZWaveMePlatform.SIREN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the siren platform."""
    setup_entry(hass, config_entry, async_add_entities, DEVICE_NAME, ZWaveMeSiren)


class ZWaveMeSiren(ZWaveMeEntity, SirenEntity):
    """Representation of a ZWaveMe siren."""

    def __init__(self, controller, device):
        """Initialize the device."""
        super().__init__(controller, device)
        self._attr_supported_features = (
            SirenEntityFeature.TURN_ON | SirenEntityFeature.TURN_OFF
        )

    @property
    def is_on(self) -> bool:
        """Return the state of the siren."""
        return self.device.level == "on"

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self.controller.zwave_api.send_command(self.device.id, "on")

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        self.controller.zwave_api.send_command(self.device.id, "off")
