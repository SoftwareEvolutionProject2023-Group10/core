"""Representation of a toggleButton."""
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ZWaveMeEntity
from .const import ZWaveMePlatform
from .helpers import setup_entry

DEVICE_NAME = ZWaveMePlatform.BUTTON


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    setup_entry(hass, config_entry, async_add_entities, DEVICE_NAME, ZWaveMeButton)


class ZWaveMeButton(ZWaveMeEntity, ButtonEntity):
    """Representation of a ZWaveMe button."""

    def press(self) -> None:
        """Turn the entity on."""
        self.controller.zwave_api.send_command(self.device.id, "on")
