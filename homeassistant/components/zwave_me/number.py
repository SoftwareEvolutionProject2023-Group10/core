"""Representation of a switchMultilevel."""
from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ZWaveMeEntity
from .const import ZWaveMePlatform
from .helpers import setup_entry

DEVICE_NAME = ZWaveMePlatform.NUMBER


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    setup_entry(hass, config_entry, async_add_entities, DEVICE_NAME, ZWaveMeNumber)


class ZWaveMeNumber(ZWaveMeEntity, NumberEntity):
    """Representation of a ZWaveMe Multilevel Switch."""

    @property
    def native_value(self) -> float:
        """Return the unit of measurement."""
        if self.device.level == 99:  # Scale max value
            return 100
        return self.device.level

    def set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.controller.zwave_api.send_command(
            self.device.id, f"exact?level={str(round(value))}"
        )
